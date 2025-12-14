// Minimal MicroPython wrapper using Web Serial to upload files and run raw repl commands.
export type SerialPort = any;
export class MicroPythonWrapper {
    port: any;
    reader: ReadableStreamDefaultReader<Uint8Array> | null = null;
    writer: WritableStreamDefaultWriter<Uint8Array> | null = null;
    decoder: TextDecoder = new TextDecoder();
    readingBuffer: string = '';
    readingUntil: string | null = null;
    resolveReadingUntilPromise: any = null;
    rejectReadingUntilPromise: any = null;
    isConnected = false;
    onDisconnect: (() => void) | null = null;

    constructor(port: any) {
        this.port = port;
    }

    async init() {
        this.reader = (this.port.readable as ReadableStream).getReader();
        this.writer = (this.port.writable as WritableStream).getWriter();
        this.isConnected = true;
        if (typeof (navigator as any).serial !== 'undefined') {
            try {
                (navigator as any).serial.addEventListener('disconnect', (ev: any) => {
                    if (ev && ev.port && ev.port === this.port) {
                        this.isConnected = false;
                        if (this.onDisconnect) this.onDisconnect();
                    }
                });
            } catch (e) { /* ignore if not supported */ }
        }
        this.readForeverAndReport();
    }

    async readForeverAndReport() {
        try {
            while (true) {
                const { value, done } = await this.reader!.read();
                if (done) {
                    this.reader!.releaseLock();
                    this.isConnected = false;
                    if (this.onDisconnect) this.onDisconnect();
                    break;
                }
                if (value) {
                    // Pass raw bytes to onData like the JS implementation
                    this.onData(value as Uint8Array);
                }
            }
        } catch (err) {
            console.warn('Read loop ended:', err);
        }
    }

    onData(buffer: Uint8Array | string) {
        // Decode here (preserves behavior when chunks split control sequences)
        let s: string;
        if (buffer instanceof Uint8Array) {
            s = this.decoder.decode(buffer);
        } else {
            s = buffer;
        }
        if (this.readingUntil != null) {
            this.readingBuffer += s;
            if (this.readingBuffer.indexOf(this.readingUntil) != -1) {
                const response = this.readingBuffer;
                this.readingUntil = null;
                this.readingBuffer = '';
                if (this.resolveReadingUntilPromise) this.resolveReadingUntilPromise(response);
            }
        }
    }

    async write(str: string) {
        const textEncoder = new TextEncoder();
        const uint8Array = textEncoder.encode(str);
        await this.writer!.write(uint8Array);
    }

    readUntil(token: string): Promise<string> {
        if (this.readingUntil != null) {
            return Promise.reject(new Error(`Already running "read until"`));
        }
        this.readingBuffer = '';
        this.readingUntil = token;
        return new Promise((resolve, reject) => {
            this.resolveReadingUntilPromise = (result: string) => {
                this.readingUntil = null;
                this.readingBuffer = '';
                this.resolveReadingUntilPromise = () => false;
                this.rejectReadingUntilPromise = () => false;
                resolve(result);
            };
            this.rejectReadingUntilPromise = (msg?: string) => {
                this.readingUntil = null;
                this.readingBuffer = '';
                this.resolveReadingUntilPromise = () => false;
                this.rejectReadingUntilPromise = () => false;
                reject(new Error(msg || 'readUntil rejected'));
            };
        });
    }

    async getPrompt() {
        if (this.readingUntil) {
            this.rejectReadingUntilPromise('Interrupt execution to get prompt');
        }
        this.write('\x03\x02');
        await this.readUntil('>>>');
    }

    async enterRawRepl() {
        this.write('\x01');
        await this.readUntil('raw REPL; CTRL-B to exit');
    }

    async exitRawRepl() {
        this.write('\x02');
        await this.readUntil('>>>');
    }

    async executeRaw(code: string): Promise<string> {
        const S = 128;
        // minimal logging: executeRaw invoked
        for (let i = 0; i < code.length; i += S) {
            const c = code.slice(i, i + S);
            await this.write(c);
            await new Promise((r) => setTimeout(r, 10));
        }
        await this.write('\x04');
        const result = await this.readUntil('\x04>');
        console.log("mpy:executeRaw result", result)
        return result;
    }

    async runHelper() {
        await this.getPrompt()
        await this.enterRawRepl()
        const out = await this.executeRaw(HELPER_CODE)
        await this.exitRawRepl()
        return out
    }

    async listFiles() {
        await this.runHelper();
        await this.enterRawRepl();
        const out = await this.executeRaw(`print(json.dumps(get_all_files("")))`);
        await this.exitRawRepl();
        // Attempt to extract JSON between OK and EOT
        const idxOk = out.indexOf('OK');
        const idxEnd = out.indexOf('\x04');
        if (idxOk === -1 || idxEnd === -1) return [];
        const result = out.slice(idxOk + 2, idxEnd);
        try { return JSON.parse(result); } catch (e) { return []; }
    }

    async createFolder(path: string) {
        await this.getPrompt()
        await this.enterRawRepl()
        let command = `import os;os.mkdir('${path}')`
        await this.executeRaw(command)
        await this.exitRawRepl()
    }

    async removeFolder(path: string) {
        await this.getPrompt()
        await this.runHelper()
        await this.enterRawRepl()
        await this.executeRaw(`delete_folder('${path}')`)
        await this.exitRawRepl()
    }

    async createFile(path: string) {
        await this.getPrompt()
        await this.enterRawRepl()
        let command = `f=open('${path}', 'w');f.close()`
        await this.executeRaw(command)
        await this.exitRawRepl()
    }

    async saveFile(path: string, content: string) {
        await this.getPrompt()
        await this.enterRawRepl()
        await this.executeRaw(`f=open('${path}','wb')\nw=f.write`)
        const d = new TextEncoder().encode(content)
        await this.executeRaw(`w(bytes([${d}]))`)
        await this.executeRaw(`f.close()`)
        await this.exitRawRepl()
    }

    async removeFile(path: string) {
        await this.getPrompt()
        await this.enterRawRepl()
        let command = `import uos\n`
        command += `try:\n`
        command += `  uos.remove("${path}")\n`
        command += `except OSError:\n`
        command += `  print(0)\n`
        await this.executeRaw(command)
        await this.exitRawRepl()
    }

    async loadFile(path: string) {
        await this.getPrompt()
        await this.enterRawRepl()
        let output = await this.executeRaw(
            `with open('${path}','r') as f:\n while 1:\n  b=f.read(256)\n  if not b:break\n  print(b,end='')`
        )
        await this.exitRawRepl()
        return extract(output)
    }

    async downloadFile(source: string) {
        await this.getPrompt();
        await this.runHelper();
        await this.enterRawRepl();
        const output = await this.executeRaw(`with open('${source}','rb') as f:\n  b = b2a_base64(f.read())\n  for i in b:\n    print( chr(i), end='' )\n`);
        await this.exitRawRepl();
        // extract between OK and EOT
        const idxOk = output.indexOf('OK');
        const idxEnd = output.indexOf('\x04');
        if (idxOk === -1 || idxEnd === -1) return '';
        const base64 = output.slice(idxOk + 2, idxEnd);
        return base64;
    }

    async downloadFileToString(source: string) {
        const base64 = await this.downloadFile(source);
        return atob(base64);
    }

    async uploadFile(path: string, content: any, reporter?: (uploaded: number, total: number) => void) {
        const CHUNK_SIZE = 512;
        reporter = reporter || (() => false);
        await this.getPrompt();
        await this.enterRawRepl();
        const safePath = path.replace(/'/g, "\\'");
        await this.executeRaw(`f=open('${safePath}','wb')\nw=f.write`);
        for (let i = 0; i < content.byteLength; i += CHUNK_SIZE) {
            const c = new Uint8Array(content.slice(i, i + CHUNK_SIZE));
            await this.executeRaw(`w(bytes([${c}]))`);
            const uploaded = Math.min(i + CHUNK_SIZE, content.byteLength);
            if (reporter) reporter(uploaded, content.byteLength);
        }
        await this.executeRaw(`f.close()`);
        await this.exitRawRepl();
    }

    async uploadFileFromString(path: string, content: string, reporter?: (uploaded: number, total: number) => void) {
        const bytes = new TextEncoder().encode(content);
        return this.uploadFile(path, bytes, reporter);
    }

    async uploadFileFromBase64(path: string, base64: string, reporter?: (uploaded: number, total: number) => void) {
        const content = Uint8Array.from(atob(base64), c => c.charCodeAt(0));
        return this.uploadFile(path, content, reporter);
    }

    async downloadFileToBytes(path: string) {
        const base64 = await this.downloadFile(path);
        const decoded = atob(base64);
        return Uint8Array.from(decoded, c => c.charCodeAt(0));
    }

    async close() {
        try {
            if (this.reader) { await this.reader.cancel(); }
        } catch (e) { }
        try { if (this.writer) { await this.writer.releaseLock(); } } catch (e) { }
        try { await this.port.close(); } catch (e) { }
        this.isConnected = false;
        if (this.onDisconnect) this.onDisconnect();
    }
}

export function extract(str: string): string {
    // Extract content between start sequence (after raw REPL prompt) and end sequence
    let startSequence = /^>+/, endSequence = /^>+/m;
    let start = str.match(startSequence)?.index ?? 0;
    if (start !== undefined) start = start + (str.match(startSequence)?.[0].length ?? 0);
    let end = str.match(endSequence)?.index;
    if (end === undefined) end = str.length;
    return str.substring(start, end).trim();
}

export const HELPER_CODE = `import os
import json
os.chdir('/')

def is_directory(path):
  return True if os.stat(path)[0] == 0x4000 else False

def get_all_files(path, array_of_files = []):
  files = os.ilistdir(path)
  for file in files:
    is_folder = file[1] == 16384
    p = path + '/' + file[0]
    array_of_files.append({
        "path": p,
        "type": "folder" if is_folder else "file"
    })
    if is_folder:
        array_of_files = get_all_files(p, array_of_files)
  return array_of_files

def ilist_all(path):
  print(json.dumps(get_all_files(path)))

def delete_folder(path):
  files = get_all_files(path)
  for file in files:
    if file['type'] == 'file':
        os.remove(file['path'])
  for file in reversed(files):
    if file['type'] == 'folder':
        os.rmdir(file['path'])
  os.rmdir(path)
`;

export function sanitizeForLog(s: string) {
    // Keep printable ASCII and common whitespace, replace other bytes with hex markers
    return s.replace(/[^\n\r\t\x20-\x7E]/g, (c) => {
        const code = c.charCodeAt(0);
        return `<0x${code.toString(16).padStart(2, '0')}>`;
    });
}