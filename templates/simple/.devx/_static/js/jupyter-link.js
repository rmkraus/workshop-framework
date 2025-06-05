/**
 * Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
 * LicenseRef-NvidiaProprietary
 *
 * NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
 * property and proprietary rights in and to this material, related
 * documentation and any modifications thereto. Any use, reproduction,
 * disclosure or distribution of this material and related documentation
 * without an express license agreement from NVIDIA CORPORATION or
 * its affiliates is strictly prohibited
 */

// Helper functions used for jupyter interactions //

async function openOrCreateFileInJupyterLab(path, factory = null, initialContent = '') {
    const app = window.parent.jupyterapp;
    if (!app) {
        console.error('JupyterLab app is not available on window.jupyterapp');
        return;
    }

    const contentsManager = app.serviceManager.contents;

    const fileExists = await checkFileExists(contentsManager, path);

    if (!fileExists) {
        // Ensure parent directories exist
        const dirPath = getParentDirectory(path);
        if (dirPath) {
            await ensureDirectoryExists(contentsManager, dirPath);
        }

        if (path.endsWith('.ipynb')) {
            await createNewNotebook(contentsManager, path);
        } else {
            await createNewFile(contentsManager, path, initialContent);
        }
    }

    await openFile(app, path, factory);
}

async function checkFileExists(contentsManager, path) {
    try {
        await contentsManager.get(path);
        console.log(`File ${path} already exists.`);
        return true;
    } catch (err) {
        if (err.response && err.response.status === 404) {
            console.log(`File ${path} does not exist.`);
            return false;
        } else {
            console.error(`Error checking file ${path}:`, err);
            throw err;
        }
    }
}

async function ensureDirectoryExists(contentsManager, dirPath) {
    const parts = dirPath.split('/');
    let currentPath = '';

    for (const part of parts) {
        currentPath = currentPath ? `${currentPath}/${part}` : part;

        try {
            await contentsManager.get(currentPath);
            console.log(`Directory ${currentPath} exists.`);
        } catch (err) {
            if (err.response && err.response.status === 404) {
                console.log(`Creating directory: ${currentPath}`);
                await contentsManager.newUntitled({
                    path: getParentDirectory(currentPath),
                    type: 'directory'
                });

                // Rename the untitled folder to the target name
                const untitledFolder = `${getParentDirectory(currentPath) ? getParentDirectory(currentPath) + '/' : ''}Untitled Folder`;
                await contentsManager.rename(untitledFolder, currentPath);
            } else {
                console.error(`Error checking/creating directory ${currentPath}:`, err);
                throw err;
            }
        }
    }
}

async function createNewNotebook(contentsManager, path) {
    const notebookContent = {
        cells: [],
        metadata: {},
        nbformat: 4,
        nbformat_minor: 5
    };

    await contentsManager.save(path, {
        type: 'notebook',
        format: 'json',
        content: notebookContent
    });

    console.log(`Created new notebook at ${path} (no kernel assigned)`);
}

async function createNewFile(contentsManager, path, initialContent = '') {
    await contentsManager.save(path, {
        type: 'file',
        format: 'text',
        content: initialContent
    });

    console.log(`Created new file at ${path}`);
}

async function openFile(app, path, factory = null) {
    const command = 'docmanager:open';
    const args = { path };
    if (factory) {
        args.factory = factory;
    }

    try {
        const widget = await app.commands.execute(command, args);
        console.log(`Opened ${path} successfully`, widget);
    } catch (error) {
        console.error(`Failed to open ${path}:`, error);
    }
}

function getParentDirectory(path) {
    const parts = path.split('/');
    parts.pop(); // remove the file name
    return parts.join('/');
}


async function goToLine(filename, lineno) {
    const app = window.parent.jupyterapp;
    if (!app) {
        console.error('JupyterLab app is not available on window.jupyterapp');
        return;
    }
    await openOrCreateFileInJupyterLab(filename);
    app.commands.execute('fileeditor:go-to-line', { line: lineno });
}


async function goToLineAndSelect(filename, searchString) {
    const app = window.parent.jupyterapp;
    if (!app) {
        console.error('JupyterLab app is not available on window.jupyterapp');
        return;
    }
    await openOrCreateFileInJupyterLab(filename);

    const widget = app.shell.currentWidget;
    const editor = widget?.content?.editor;
    const blocks = editor?.doc?.children;

    if (!editor || !blocks || !Array.isArray(blocks)) {
        console.error("No suitable editor or document found.");
        return;
    }

    // Flatten all lines across all blocks, tracking line numbers
    let totalLine = 0;
    for (const block of blocks) {
        const lines = block.text;
        for (let i = 0; i < lines.length; i++) {
            if (lines[i].includes(searchString)) {
                const matchLine = totalLine;

                // Select and scroll to the matched line
                selection = {
                    start: { line: matchLine, column: 0 },
                    end: { line: matchLine, column: lines[i].length }
                }
                await app.commands.execute('fileeditor:go-to-line', { line: matchLine });
                editor.setSelection(selection);
                return;
            }
            totalLine++;
        }
    }

    console.warn(`"${searchString}" not found.`);
}


async function openNewTerminal() {
    const app = window.parent.jupyterapp;
    if (!app) {
        console.error('JupyterLab app is not available on window.jupyterapp');
        return;
    }

    try {
        const widget = await app.commands.execute('terminal:create-new');
        console.log('New terminal opened successfully', widget);
        return widget;
    } catch (error) {
        console.error('Failed to open new terminal:', error);
    }
}
