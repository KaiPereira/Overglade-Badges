import { MicroPythonWrapper, type SerialPort, sanitizeForLog } from './micropython-webserial.ts'

let port: SerialPort | null = null;
let mp: MicroPythonWrapper | null = null;
// Whether we're currently performing an upload or other write operation
let isUploading = false;
// Track overall bytes for progress across upload flow
let totalBytes = 0;

const btn = document.getElementById("connect-button") as HTMLButtonElement;
const filters = [
    { usbVendorId: 0x2E8A, usbProductId: 0x0005 }
]

if (btn) {
    btn.addEventListener("click", async (e: Event) => {
        e.preventDefault();
        e.stopPropagation();
        if (!("serial" in navigator)) {
            console.error("Web Serial API not supported.");
            return;
        }

        // If we already have an active MicroPython wrapper and it's connected, disconnect
        if (mp && mp.isConnected) {
            if (isUploading) {
                const ok = confirm('An upload/write is currently in progress. Disconnecting will abort it and may leave the badge in an inconsistent state. Do you want to continue?');
                if (!ok) return;
            }
            try {
                if (mp) {
                    try { await mp.close(); } catch (e) { }
                }
                // close the underlying port
                try { await port.close(); } catch (e) { }
                mp = null;
                port = null;
                setDisconnectedAppearance();
                appendOrUpdateLog('connection','Disconnected.');
            } catch (err) {
                console.error("Disconnect failed:", err);
            }
            return;
        }

        // Otherwise, attempt connection
        try {
            port = await (navigator as any).serial.requestPort({ filters });
            await port.open({ baudRate: 115200 });

            // Setup wrapper
            mp = new MicroPythonWrapper(port as any);
            mp.onDisconnect = () => {
                // ensure UI updates
                mp = null;
                port = null;
                updateConnectButtonAppearance();
            };
            await mp.init();
            // Try to pre-load existing configuration & version, if present
            try {
                const cfg = await mp.downloadFileToString('/config.json');
                if (cfg) {
                    const parsed = JSON.parse(cfg);
                    (document.getElementById('userName') as HTMLInputElement).value = parsed.userName || '';
                    (document.getElementById('userHandle') as HTMLInputElement).value = parsed.userHandle || '';
                    (document.getElementById('userPronouns') as HTMLInputElement).value = parsed.userPronouns || '';
                }
            } catch (e) { /* ignore if not present */ }
            try {
                const version = await mp.downloadFileToString('/VERSION');
                if (version) {
                    console.log('Device firmware version:', version);
                }
            } catch (e) { }

            updateConnectButtonAppearance();
            appendOrUpdateLog('connection', 'Connected');
        } catch (err) {
            console.warn("Connection failed or cancelled:", err);
        }
    });
}

// UI helpers

function setConnectedAppearance() {
    btn.textContent = "Disconnect";
    btn.classList.remove("bg-green-700", "hover:bg-green-600");
    btn.classList.add("bg-red-900", "hover:bg-red-700");
    if (saveConfigButton) saveConfigButton.disabled = false;
    if (loadConfigButton) loadConfigButton.disabled = false;
    if (uploadFirmwareButton) uploadFirmwareButton.disabled = false;
    if (wipeBadgeButton) wipeBadgeButton.disabled = false;
    // update textual status indicator
    const statusText = document.getElementById('connection-text');
    const dot = document.getElementById('connection-dot');
    if (statusText) statusText.textContent = 'Connected';
    if (dot) {
        dot.classList.remove('bg-red-500');
        dot.classList.add('bg-green-500');
    }
    setUIFieldsEnabled(true);
}

function setDisconnectedAppearance() {
    btn.textContent = "Connect";
    btn.classList.remove("bg-red-900", "hover:bg-red-700");
    btn.classList.add("bg-green-700", "hover:bg-green-600");
    if (saveConfigButton) saveConfigButton.disabled = true;
    if (loadConfigButton) loadConfigButton.disabled = true;
    if (uploadFirmwareButton) uploadFirmwareButton.disabled = true;
    if (wipeBadgeButton) wipeBadgeButton.disabled = true;
    const statusText = document.getElementById('connection-text');
    const dot = document.getElementById('connection-dot');
    if (statusText) statusText.textContent = 'Disconnected';
    if (dot) {
        dot.classList.remove('bg-green-500');
        dot.classList.add('bg-red-500');
    }
    setUIFieldsEnabled(false);
}

function setUIFieldsEnabled(enabled: boolean) {
    // Text inputs
    const userNameEl = document.getElementById('userName') as HTMLInputElement | null;
    const userHandleEl = document.getElementById('userHandle') as HTMLInputElement | null;
    const userPronounsEl = document.getElementById('userPronouns') as HTMLInputElement | null;
    if (userNameEl) { userNameEl.disabled = !enabled; userNameEl.classList.toggle('opacity-50', !enabled); userNameEl.classList.toggle('cursor-not-allowed', !enabled); }
    if (userHandleEl) { userHandleEl.disabled = !enabled; userHandleEl.classList.toggle('opacity-50', !enabled); userHandleEl.classList.toggle('cursor-not-allowed', !enabled); }
    if (userPronounsEl) { userPronounsEl.disabled = !enabled; userPronounsEl.classList.toggle('opacity-50', !enabled); userPronounsEl.classList.toggle('cursor-not-allowed', !enabled); }

    // File input + firmware actions
    if (firmwareInput) {
        firmwareInput.disabled = !enabled;
        firmwareInput.classList.toggle('opacity-50', !enabled);
        firmwareInput.classList.toggle('cursor-not-allowed', !enabled);
        firmwareInput.classList.toggle('pointer-events-none', !enabled);
    }
    // keep choose firmware available even when disconnected (allows offline staging)
    if (chooseFirmwareButton) {
        chooseFirmwareButton.classList.toggle('opacity-50', false);
        chooseFirmwareButton.classList.remove('cursor-not-allowed');
        chooseFirmwareButton.classList.remove('pointer-events-none');
        chooseFirmwareButton.classList.toggle('cursor-pointer', true);
    }
    // allow 'Load firmware' offline as well
    if (loadFirmwareButton) {
        loadFirmwareButton.classList.toggle('opacity-50', false);
        loadFirmwareButton.classList.remove('cursor-not-allowed');
        loadFirmwareButton.classList.remove('pointer-events-none');
        loadFirmwareButton.classList.toggle('cursor-pointer', true);
    }
    if (uploadFirmwareButton) {
        uploadFirmwareButton.disabled = !enabled;
        uploadFirmwareButton.classList.toggle('opacity-50', !enabled);
        uploadFirmwareButton.classList.toggle('cursor-not-allowed', !enabled);
        uploadFirmwareButton.classList.toggle('pointer-events-none', !enabled);
        uploadFirmwareButton.classList.toggle('cursor-pointer', enabled);
    }

    // Config controls
    if (saveConfigButton) {
        saveConfigButton.disabled = !enabled;
        saveConfigButton.classList.toggle('opacity-50', !enabled);
        saveConfigButton.classList.toggle('cursor-not-allowed', !enabled);
        saveConfigButton.classList.toggle('pointer-events-none', !enabled);
        saveConfigButton.classList.toggle('cursor-pointer', enabled);
    }
    if (loadConfigButton) {
        loadConfigButton.disabled = !enabled;
        loadConfigButton.classList.toggle('opacity-50', !enabled);
        loadConfigButton.classList.toggle('cursor-not-allowed', !enabled);
        loadConfigButton.classList.toggle('pointer-events-none', !enabled);
        loadConfigButton.classList.toggle('cursor-pointer', enabled);
    }

    // Wipe and update
    if (wipeBadgeButton) {
        wipeBadgeButton.disabled = !enabled;
        wipeBadgeButton.classList.toggle('opacity-50', !enabled);
        wipeBadgeButton.classList.toggle('cursor-not-allowed', !enabled);
        wipeBadgeButton.classList.toggle('pointer-events-none', !enabled);
        wipeBadgeButton.classList.toggle('cursor-pointer', enabled);
    }
    // Keep checking for updates available even if not connected; do not disable updateBtn
}

function updateConnectButtonAppearance() {
    if (mp && mp.isConnected) {
        setConnectedAppearance();
    } else {
        setDisconnectedAppearance();
    }
}

// Listen for serial events (connect/disconnect) if supported to update UI
if (typeof (navigator as any).serial !== 'undefined') {
    try {
        (navigator as any).serial.addEventListener('connect', () => {
            updateConnectButtonAppearance();
        });
        (navigator as any).serial.addEventListener('disconnect', (ev: any) => {
            if (ev && ev.port && ev.port === port) {
                if (mp) {
                    try { mp.isConnected = false; } catch (e) { }
                }
                mp = null;
                port = null;
                updateConnectButtonAppearance();
            }
        });
    } catch (e) { /* not supported in some browsers */ }
}

// Close the port if the page unloads
window.addEventListener('beforeunload', (e) => {
    if (isUploading) {
        // Prevent accidental navigation during an upload
        e.preventDefault();
        (e as any).returnValue = '';
        return;
    }
    if (mp) {
        try { mp.close(); } catch (e) { }
    }
});

// UI wiring and features
const saveConfigButton = document.getElementById('save-config') as HTMLButtonElement | null;
const updateBtn = document.getElementById('update-button') as HTMLButtonElement | null;
const loadConfigButton = document.getElementById('load-config') as HTMLButtonElement | null;
const firmwareInput = document.getElementById('firmware-input') as HTMLInputElement | null;
const chooseFirmwareButton = document.getElementById('choose-firmware') as HTMLButtonElement | null;
const firmwareFilenameEl = document.getElementById('firmware-filename') as HTMLSpanElement | null;
const loadFirmwareButton = document.getElementById('load-firmware') as HTMLButtonElement | null;
const uploadFirmwareButton = document.getElementById('upload-firmware') as HTMLButtonElement | null;
const wipeBadgeButton = document.getElementById('wipe-badge') as HTMLButtonElement | null;

let firmwareFiles: { path: string, content: Uint8Array, folder: string }[] = [];

function getFolder(path: string) {
    const idx = path.lastIndexOf('/');
    if (idx <= 0) return '/';
    return path.slice(0, idx);
}

if (saveConfigButton) {
    saveConfigButton.addEventListener('click', async (e: Event) => {
        e.preventDefault();
        e.stopPropagation();
        if (!mp) { alert('Not connected'); return; }
        if (isUploading) { if (!confirm('An upload is currently in progress. Overwriting configuration now will interrupt it. Continue?')) return; }
        const userName = (document.getElementById('userName') as HTMLInputElement).value || '';
        const userHandle = (document.getElementById('userHandle') as HTMLInputElement).value || '';
        const userPronouns = (document.getElementById('userPronouns') as HTMLInputElement).value || '';
        const data = { userName, userHandle, userPronouns };
        try {
            isUploading = true;
            if (progressBar) progressBar.value = 0;
            await mp.uploadFileFromString('/config.json', JSON.stringify(data, null, 2), (uploaded, total) => {
                const perc = Math.round((uploaded / total) * 100);
                appendOrUpdateLog('config', `Saving config: ${perc}% (${uploaded}/${total})`);
                if (progressBar) progressBar.value = perc;
            });
            alert('Configuration saved');
        } catch (err) {
            console.error('Failed to save configuration', err);
            appendOrUpdateLog('config', `Save failed: ${err}`);
            alert('Failed to save configuration: ' + err);
        } finally {
            if (saveConfigButton) saveConfigButton.disabled = false;
            isUploading = false;
            if (progressBar) progressBar.value = 0;
            appendOrUpdateLog('config', `Config save completed`);
        }
    });
}

if (loadConfigButton) {
    loadConfigButton.addEventListener('click', async (e: Event) => {
        e.preventDefault();
        e.stopPropagation();
        if (!mp) { alert('Not connected'); return; }
        try {
            if (progressBar) progressBar.value = 0;
            appendOrUpdateLog('config', 'Loading config...');
            const content = await mp.downloadFileToString('/config.json');
            if (progressBar) progressBar.value = 100;
            const parsed = JSON.parse(content);
            (document.getElementById('userName') as HTMLInputElement).value = parsed.userName || '';
            (document.getElementById('userHandle') as HTMLInputElement).value = parsed.userHandle || '';
            (document.getElementById('userPronouns') as HTMLInputElement).value = parsed.userPronouns || '';
            alert('Configuration loaded');
        } catch (err) {
            console.error('Failed to load configuration', err);
            alert('Failed to load configuration: ' + (err as any).message || err);
        }
    });
}

if (loadFirmwareButton && firmwareInput) {
    loadFirmwareButton.addEventListener('click', async (e: Event) => {
        e.preventDefault();
        e.stopPropagation();
        const files = firmwareInput.files;
        if (!files || !files[0]) { alert('Please choose a firmware file (.zip or single file)'); return; }
        const file = files[0];
        if (file.name.endsWith('.zip')) {
            // @ts-ignore - dynamically import jszip
            const JSZip = (await import('jszip')).default;
            const jszip = new JSZip();
            const zip = await jszip.loadAsync(file);
            firmwareFiles = [];
            const zipFiles = zip.files as any;
            for (const path in zipFiles) {
                const entry = zipFiles[path] as any;
                if (entry.dir) { continue; }
                const content = await entry.async('uint8array');
                const p = '/' + path;
                firmwareFiles.push({ path: p, content, folder: getFolder(p) });
            }
            // Deduplicate by path in case any duplicates exist in the zip
            {
                const map = new Map<string, Uint8Array>();
                for (const f of firmwareFiles) {
                    map.set(f.path, f.content);
                }
                firmwareFiles = [...map.entries()].map(([path, content]) => ({ path, content, folder: getFolder(path) }));
            }
            // Move VERSION file to end so we upload it last
            const versionIndex = firmwareFiles.findIndex(f => f.path === '/VERSION');
            if (versionIndex !== -1) {
                const [versionFile] = firmwareFiles.splice(versionIndex, 1);
                firmwareFiles.push(versionFile);
            }
            console.log('Loaded firmware files:', firmwareFiles.map(f => f.path));
            alert('Firmware loaded (' + firmwareFiles.length + ' files)');
        } else {
            const buf = new Uint8Array(await file.arrayBuffer());
            const p = '/' + file.name;
            firmwareFiles = [{ path: p, content: buf, folder: getFolder(p) }];
            console.log('Loaded single firmware', firmwareFiles[0].path);
            alert('Firmware loaded: ' + file.name);
        }
    });
}

// Wire up the choose button and show filename when user selects a file
if (chooseFirmwareButton && firmwareInput) {
    chooseFirmwareButton.addEventListener('click', (e: Event) => {
        e.preventDefault();
        e.stopPropagation();
        firmwareInput.click();
    });
    firmwareInput.addEventListener('change', () => {
        const files = firmwareInput.files;
        if (!files || !files[0]) {
            if (firmwareFilenameEl) firmwareFilenameEl.textContent = 'No file chosen';
            return;
        }
        const file = files[0];
        if (firmwareFilenameEl) firmwareFilenameEl.textContent = file.name;
    });
}

if (uploadFirmwareButton) {
    uploadFirmwareButton.addEventListener('click', async (e: Event) => {
        e.preventDefault();
        e.stopPropagation();
        if (!mp) { alert('Not connected'); return; }
        if (!firmwareFiles || firmwareFiles.length === 0) { alert('No firmware loaded'); return; }
        try {
            isUploading = true;
            clearLog();
            appendOrUpdateLog('overall', 'Starting firmware upload...');

            appendOrUpdateLog('overall', `Firmware upload will include ${firmwareFiles.length} unique files`);

            // compute total bytes for overall progress
            totalBytes = firmwareFiles.reduce((s, ff) => s + ff.content.byteLength, 0);


            for (const file of firmwareFiles) {
                appendLog(`Uploading ${file.path} (${file.content.byteLength} bytes)...`);
            }

            appendLog('Firmware uploaded (attempted).');
            try {
                isUploading = true;
                clearLog();
                appendOrUpdateLog('overall', 'Starting firmware upload...');

                appendOrUpdateLog('overall', `Firmware upload will include ${firmwareFiles.length} unique files`);

                // compute total bytes for overall progress
                totalBytes = firmwareFiles.reduce((s, ff) => s + ff.content.byteLength, 0);

                // Create folders first (unique, excluding root)
                const folderSet = new Set<string>(firmwareFiles.map(f => f.folder || '/'));
                const folders = Array.from(folderSet).filter(f => f && f !== '/');
                // sort by depth so parents are created before children
                folders.sort((a, b) => a.split('/').length - b.split('/').length);
                for (const folder of folders) {
                    appendLog(`Creating folder ${folder}...`);
                    await mp.createFolder(folder);
                }

                for (const file of firmwareFiles) {
                    await mp.uploadFile(file.path, file.content, (uploaded, total) => {
                        const perc = Math.round((uploaded / total) * 100);
                        appendOrUpdateLog(file.path, `Uploading ${file.path}: ${perc}% (${uploaded}/${total})`);
                    });
                }

                appendLog('Firmware uploaded successfully.');
                if (progressBar) progressBar.value = 100;
                appendOrUpdateLog('overall', `Overall: 100% (${totalBytes}/${totalBytes} bytes)`);
            } catch (err) {
                console.error('Upload failed', err);
                appendLog('Upload failed: ' + err);
                alert('Upload failed: ' + err);
            } finally {
                if (wipeBadgeButton) wipeBadgeButton.disabled = false;
                isUploading = false;
                if (uploadFirmwareButton) uploadFirmwareButton.disabled = false;
                setTimeout(() => {
                    if (progressBar) progressBar.value = 0;
                }, 2000);
                appendLog('Upload process completed.');
            }
        } catch (err) {
            console.error('Wipe failed', err);
            appendLog('Wipe failed: ' + err);
            appendOrUpdateLog('wipe', 'Wipe failed: ' + err);
            alert('Wipe failed: ' + err);
        } finally {
            isUploading = false;
            if (wipeBadgeButton) wipeBadgeButton.disabled = false;
            if (progressBar) progressBar.value = 0;
        }
    });
}
// Wipe button: delete all files/folders on the device (destructive)
if (wipeBadgeButton) {
    wipeBadgeButton.addEventListener('click', async (e: Event) => {
        e.preventDefault();
        e.stopPropagation();
        if (!mp) { alert('Not connected'); return; }
        if (isUploading) {
            if (!confirm('An upload/write is currently in progress. Wiping now will abort it. Continue?')) return;
        }
        if (!confirm('This will delete all files on the badge. Are you sure you want to continue?')) return;
        try {
            isUploading = true;
            if (wipeBadgeButton) wipeBadgeButton.disabled = true;
            clearLog();
            appendOrUpdateLog('wipe', 'Starting wipe...');
            appendLog('Wiping device filesystem...');
            // removeFolder('/') will delete contents but won't remove the root directory
            await mp.removeFolder('/');
            appendLog('Wipe completed.');
            appendOrUpdateLog('wipe', 'Wipe completed.');
            alert('Wipe completed');
        } catch (err) {
            console.error('Wipe failed', err);
            appendLog('Wipe failed: ' + err);
            appendOrUpdateLog('wipe', 'Wipe failed: ' + err);
            alert('Wipe failed: ' + err);
        } finally {
            isUploading = false;
            if (wipeBadgeButton) wipeBadgeButton.disabled = false;
            if (progressBar) progressBar.value = 0;
        }
    });
}
if (updateBtn) {
    updateBtn.addEventListener('click', async (e: Event) => {
        e.preventDefault();
        e.stopPropagation();
        clearLog();
        appendLog('Checking for updates...');
        // Attempt to fetch latest firmware zip from the reference repo (if hosted)
        try {
            updateBtn.disabled = true;
            updateBtn.textContent = 'Checking...';

            firmwareFiles = [];

            // Preferred method: fetch files directly from the code/embedded folder (recursive)
            const dirUrl = 'https://api.github.com/repos/mpkendall/prototype-badge/contents/code/embedded?ref=main';
            let resp = await fetch(dirUrl);
            if (resp.ok) {
                // Recursively traverse directories to find files and keep folder structure
                async function fetchGitHubDir(path: string) {
                    const url = `https://api.github.com/repos/mpkendall/prototype-badge/contents/${encodeURIComponent(path)}?ref=main`;
                    const r = await fetch(url);
                    if (!r.ok) throw new Error('Failed to fetch ' + url + ': ' + r.statusText);
                    const listing = await r.json();
                    if (!Array.isArray(listing)) throw new Error('Unexpected directory listing for ' + path);
                    for (const item of listing) {
                        if (item.type === 'file') {
                            if (!item.download_url) continue;
                            // skip macOS system files and folder metadata
                            if ((item.path && item.path.indexOf('__MACOSX') !== -1) || (item.name && item.name.endsWith('.DS_Store'))) continue;
                            try {
                                const fileResp = await fetch(item.download_url);
                                if (!fileResp.ok) continue;
                                const arrayBuf = await fileResp.arrayBuffer();
                                const content = new Uint8Array(arrayBuf);
                                // compute path relative to code/embedded and keep structure
                                const rel = item.path.replace(/^code\/embedded\/?/, '');
                                const p = '/' + rel;
                                firmwareFiles.push({ path: p, content, folder: getFolder(p) });
                            } catch (e) {
                                console.warn('Failed to download file', item.download_url, e);
                                continue;
                            }
                        } else if (item.type === 'dir') {
                            // recurse into subdirectory
                            await fetchGitHubDir(item.path);
                        }
                    }
                }
                try {
                    await fetchGitHubDir('code/embedded');
                } catch (err) {
                    // If recursive fetch fails, fall back to the original behavior by trying to read the top level listing entries
                    console.warn('Recursive fetch failed, falling back to listing:', err);
                    const listing = await resp.json();
                    if (!Array.isArray(listing)) throw new Error('Unexpected directory listing');
                    for (const item of listing) {
                        if (item.type !== 'file') continue;
                        if (!item.download_url) continue;
                        const fileResp = await fetch(item.download_url);
                        if (!fileResp.ok) continue;
                        const arrayBuf = await fileResp.arrayBuffer();
                        const content = new Uint8Array(arrayBuf);
                        const p = '/' + item.name;
                        firmwareFiles.push({ path: p, content, folder: getFolder(p) });
                    }
                }
            } else {
                // Fallback: look for a single firmware zip in the code folder
                const zipUrl = 'https://api.github.com/repos/mpkendall/prototype-badge/contents/code/embedded/firmware.zip?ref=main';
                resp = await fetch(zipUrl);
                if (resp.ok) {
                    const json = await resp.json();
                    if (!json.content) throw new Error('No content available in firmware.zip');
                    const b64 = json.content;
                    const binary = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
                    const blob = new Blob([binary]);
                    // parse zip content
                    // @ts-ignore
                    const JSZip = (await import('jszip')).default;
                    const jszip = new JSZip();
                    const zip = await jszip.loadAsync(blob);
                    const zipFiles = zip.files as any;
                    for (const path in zipFiles) {
                        const entry = zipFiles[path] as any;
                        if (entry.dir) continue;
                        if (path.startsWith('__MACOSX') || path.endsWith('.DS_Store')) continue;
                        const content = await entry.async('uint8array');
                        const p = '/' + path;
                        firmwareFiles.push({ path: p, content, folder: getFolder(p) });
                    }
                } else {
                    throw new Error('Firmware fetch failed: ' + resp.statusText);
                }
            }
            // Move VERSION to end
            const versionIndex = firmwareFiles.findIndex(f => f.path === '/VERSION');
            if (versionIndex !== -1) {
                const [versionFile] = firmwareFiles.splice(versionIndex, 1);
                firmwareFiles.push(versionFile);
            }
            appendOrUpdateLog('files', `files: ${firmwareFiles.map(f => f.path).join(', ')}`);
            appendOrUpdateLog('folders', `folders: ${Array.from(new Set(firmwareFiles.map(f => f.folder))).join(', ')}`);
            appendLog('Latest firmware fetched and loaded (' + firmwareFiles.length + ' files)');
        } catch (err) {
            console.error('Update failed', err);
            alert('Update failed: ' + err);
        } finally {
            updateBtn.disabled = false;
            updateBtn.textContent = 'Check for Updates';
        }
    });
}
// Help modal wiring
const helpButton = document.getElementById('help-button') as HTMLButtonElement | null;
const helpModal = document.getElementById('help-modal') as HTMLDivElement | null;
const helpClose = document.getElementById('help-close') as HTMLButtonElement | null;
const helpOverlay = document.getElementById('help-overlay') as HTMLDivElement | null;

function openHelp() {
    if (!helpModal || !helpButton) return;
    helpModal.classList.remove('opacity-0', 'pointer-events-none');
    helpModal.classList.add('flex');
    helpButton.setAttribute('aria-expanded', 'true');
}

function closeHelp() {
    if (!helpModal || !helpButton) return;
    helpModal.classList.add('opacity-0', 'pointer-events-none');
    helpModal.classList.remove('flex');
    helpButton.setAttribute('aria-expanded', 'false');
}

if (helpButton) {
    helpButton.addEventListener('click', (e: Event) => {
        e.preventDefault();
        e.stopPropagation();
        // Toggle by checking our visibility classes
        if (helpModal && helpModal.classList.contains('opacity-0')) {
            openHelp();
        } else {
            closeHelp();
        }
    });
}

if (helpClose) {
    helpClose.addEventListener('click', (e: Event) => { e.preventDefault(); closeHelp(); });
}
if (helpOverlay) {
    helpOverlay.addEventListener('click', (e: Event) => { e.preventDefault(); closeHelp(); });
}
window.addEventListener('keydown', (e: KeyboardEvent) => {
    if (e.key === 'Escape') closeHelp();
});
// Update UI initial state now that elements exist
updateConnectButtonAppearance();

// Logging below the Update button
const logBox = document.createElement('div');
logBox.id = 'update-log';
logBox.className = 'mt-3 bg-black/10 p-2 rounded text-sm font-mono max-h-40 overflow-auto text-stone-300';
const updateButtonWrapper = document.getElementById('update-button')?.parentElement;
if (updateButtonWrapper) updateButtonWrapper.appendChild(logBox);

// Add a progress bar for overall progress
const progressBar = document.createElement('progress');
progressBar.id = 'update-progress';
progressBar.max = 100;
progressBar.value = 0;
progressBar.className = 'w-full mt-2 h-2';
if (updateButtonWrapper) updateButtonWrapper.appendChild(progressBar);

const logEntries = new Map<string, HTMLDivElement>();

function appendLog(msg: string) {
    const line = document.createElement('div');
    line.textContent = sanitizeForLog(msg);
    logBox.appendChild(line);
    logBox.scrollTop = logBox.scrollHeight;
}

function appendOrUpdateLog(key: string, msg: string) {
    const safe = sanitizeForLog(msg);
    if (logEntries.has(key)) {
        const el = logEntries.get(key)!;
        el.textContent = safe;
    } else {
        const el = document.createElement('div');
        el.id = `log-${Math.random().toString(36).slice(2)}`;
        el.textContent = safe;
        logEntries.set(key, el);
        logBox.appendChild(el);
    }
    logBox.scrollTop = logBox.scrollHeight;
}

function clearLog() {
    if (logBox) logBox.innerHTML = '';
    logEntries.clear();
    if (progressBar) progressBar.value = 0;
}