// Custom JavaScript for FrameWork documentation

document.addEventListener('DOMContentLoaded', function() {
    // Add category badges to protocol tables
    enhanceProtocolTables();
    
    // Add copy buttons to code blocks without them
    enhanceCodeBlocks();
    
    // Smooth scroll for anchor links
    enhanceAnchorLinks();
    
    // Add keyboard shortcuts hint
    addKeyboardShortcuts();
});

function enhanceProtocolTables() {
    // Find tables with protocol data and add visual badges
    document.querySelectorAll('table').forEach(table => {
        const headers = Array.from(table.querySelectorAll('th')).map(th => th.textContent.trim().toLowerCase());
        
        const categoryIdx = headers.indexOf('category');
        const difficultyIdx = headers.indexOf('difficulty');
        
        if (categoryIdx === -1 && difficultyIdx === -1) return;
        
        table.querySelectorAll('tbody tr').forEach(row => {
            const cells = row.querySelectorAll('td');
            
            if (categoryIdx !== -1 && cells[categoryIdx]) {
                const category = cells[categoryIdx].textContent.trim();
                const badge = createCategoryBadge(category);
                cells[categoryIdx].innerHTML = '';
                cells[categoryIdx].appendChild(badge);
            }
            
            if (difficultyIdx !== -1 && cells[difficultyIdx]) {
                const difficulty = cells[difficultyIdx].textContent.trim();
                const badge = createDifficultyBadge(difficulty);
                cells[difficultyIdx].innerHTML = '';
                cells[difficultyIdx].appendChild(badge);
            }
        });
    });
}

function createCategoryBadge(category) {
    const badge = document.createElement('span');
    badge.className = `category-badge category-${category.toLowerCase().replace(/[^a-z]+/g, '-')}`;
    badge.textContent = category;
    return badge;
}

function createDifficultyBadge(difficulty) {
    const badge = document.createElement('span');
    badge.className = `difficulty-badge difficulty-${difficulty.toLowerCase()}`;
    badge.textContent = difficulty;
    return badge;
}

function enhanceCodeBlocks() {
    // Material theme already adds copy buttons, but we can add language labels
    document.querySelectorAll('pre code').forEach(block => {
        const lang = block.className.match(/language-(\w+)/);
        if (lang && !block.parentElement.dataset.languageLabel) {
            block.parentElement.dataset.languageLabel = lang[1];
        }
    });
}

function enhanceAnchorLinks() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href').slice(1);
            const target = document.getElementById(targetId);
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                history.pushState(null, null, this.getAttribute('href'));
            }
        });
    });
}

function addKeyboardShortcuts() {
    // Add ? key to show shortcuts
    document.addEventListener('keydown', function(e) {
        if (e.key === '?' && (e.metaKey || e.ctrlKey)) {
            e.preventDefault();
            showShortcutsModal();
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            closeShortcutsModal();
        }
    });
}

function showShortcutsModal() {
    if (document.getElementById('shortcuts-modal')) return;
    
    const modal = document.createElement('div');
    modal.id = 'shortcuts-modal';
    modal.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: var(--md-default-bg-color);
        border: 1px solid var(--md-default-fg-color--lightest);
        border-radius: 8px;
        padding: 1.5rem;
        max-width: 400px;
        width: 90%;
        z-index: 1000;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
    `;
    
    modal.innerHTML = `
        <h3 style="margin-top: 0;">Keyboard Shortcuts</h3>
        <dl style="margin: 0;">
            <dt>?</dt><dd>Show this help</dd>
            <dt>Esc</dt><dd>Close modal / search</dd>
            <dt>s</dt><dd>Focus search</dd>
            <dt>g then h</dt><dd>Go to home</dd>
            <dt>g then a</dt><dd>Go to API reference</dd>
            <dt>g then r</dt><dd>Go to Architecture</dd>
            <dt>g then p</dt><dd>Go to Protocol Database</dd>
            <dt>g then d</dt><dd>Go to Development</dd>
            <dt>g then l</dt><dd>Go to Releases</dd>
        </dl>
        <p style="margin-top: 1rem; font-size: 0.85rem; color: var(--md-default-fg-color--light);">
            Press <kbd>Esc</kbd> or click outside to close
        </p>
    `;
    
    const overlay = document.createElement('div');
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.5);
        z-index: 999;
    `;
    overlay.onclick = closeShortcutsModal;
    
    document.body.appendChild(overlay);
    document.body.appendChild(modal);
    modal.focus();
}

function closeShortcutsModal() {
    const modal = document.getElementById('shortcuts-modal');
    const overlay = modal?.previousElementSibling;
    if (overlay && overlay.style.position === 'fixed') overlay.remove();
    if (modal) modal.remove();
}

// Add search analytics (optional)
function trackSearch(query) {
    // Could send to analytics endpoint
    console.debug('Search:', query);
}

// Observe search input
const searchObserver = new MutationObserver(mutations => {
    mutations.forEach(mutation => {
        if (mutation.type === 'attributes' && mutation.attributeName === 'value') {
            const input = mutation.target;
            if (input.matches('.md-search__input')) {
                trackSearch(input.value);
            }
        }
    });
});

document.querySelectorAll('.md-search__input').forEach(input => {
    searchObserver.observe(input, { attributes: true });
});