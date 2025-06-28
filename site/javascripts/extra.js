// ===== NetApp ActiveIQ API Documentation Enhanced JavaScript =====

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all enhanced features
    initializeAPIEndpointStyling();
    initializeQuickRefCards();
    initializeCodeCopyEnhancements();
    initializeSearchEnhancements();
    initializeProgressIndicators();
    initializeInteractiveElements();
    initializeTableEnhancements();
    initializeBadges();
    initializeScrollAnimations();
    initializeThemeToggleEnhancements();
});

// API Endpoint Styling Enhancement
function initializeAPIEndpointStyling() {
    // Find all code blocks that contain API calls
    const codeBlocks = document.querySelectorAll('pre code');
    
    codeBlocks.forEach(block => {
        const text = block.textContent;
        
        // Detect API endpoints in code blocks
        if (text.includes('curl') || text.includes('GET') || text.includes('POST') || text.includes('PATCH') || text.includes('DELETE')) {
            enhanceAPICodeBlock(block);
        }
    });
}

function enhanceAPICodeBlock(block) {
    const text = block.innerHTML;
    
    // Add styling for HTTP methods
    const methodRegex = /(GET|POST|PATCH|DELETE|PUT)\s/g;
    const styledText = text.replace(methodRegex, '<span class="api-method $1">$1</span> ');
    
    // Add styling for status codes
    const statusRegex = /(\d{3})/g;
    const finalText = styledText.replace(statusRegex, (match) => {
        const code = parseInt(match);
        let className = 'status-code';
        if (code >= 200 && code < 300) className += ' success';
        else if (code >= 400 && code < 500) className += ' warning';
        else if (code >= 500) className += ' error';
        return `<span class="${className}">${match}</span>`;
    });
    
    block.innerHTML = finalText;
}

// Quick Reference Cards Enhancement
function initializeQuickRefCards() {
    const tables = document.querySelectorAll('table');
    
    tables.forEach(table => {
        if (table.querySelector('th') && table.querySelector('th').textContent.includes('Endpoint')) {
            wrapTableInCard(table, 'API Endpoints Quick Reference');
        }
        if (table.querySelector('th') && table.querySelector('th').textContent.includes('Model')) {
            wrapTableInCard(table, 'Data Models Quick Reference');
        }
    });
}

function wrapTableInCard(table, title) {
    const card = document.createElement('div');
    card.className = 'quick-ref-card';
    
    const cardTitle = document.createElement('h3');
    cardTitle.textContent = title;
    
    table.parentNode.insertBefore(card, table);
    card.appendChild(cardTitle);
    card.appendChild(table);
}

// Enhanced Code Copy Functionality
function initializeCodeCopyEnhancements() {
    // Add copy buttons to code blocks without them
    const codeBlocks = document.querySelectorAll('pre:not(.md-clipboard)');
    
    codeBlocks.forEach(block => {
        if (!block.querySelector('.md-clipboard')) {
            addCopyButton(block);
        }
    });
}

function addCopyButton(codeBlock) {
    const button = document.createElement('button');
    button.className = 'md-clipboard md-icon';
    button.title = 'Copy to clipboard';
    button.innerHTML = '📋';
    
    button.addEventListener('click', () => {
        const code = codeBlock.querySelector('code');
        if (code) {
            navigator.clipboard.writeText(code.textContent).then(() => {
                showCopyFeedback(button);
            });
        }
    });
    
    codeBlock.style.position = 'relative';
    codeBlock.appendChild(button);
}

function showCopyFeedback(button) {
    const originalText = button.innerHTML;
    button.innerHTML = '✓';
    button.style.background = 'var(--success-color)';
    
    setTimeout(() => {
        button.innerHTML = originalText;
        button.style.background = '';
    }, 2000);
}

// Search Enhancement
function initializeSearchEnhancements() {
    const searchInput = document.querySelector('.md-search__input');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(enhanceSearchResults, 300));
    }
}

function enhanceSearchResults() {
    const results = document.querySelectorAll('.md-search__result');
    results.forEach(result => {
        const link = result.querySelector('a');
        if (link) {
            // Add category badges to search results
            const href = link.getAttribute('href');
            if (href.includes('api-endpoints')) {
                addResultBadge(result, 'API', 'badge-info');
            } else if (href.includes('data-models')) {
                addResultBadge(result, 'Models', 'badge-warning');
            } else if (href.includes('examples')) {
                addResultBadge(result, 'Examples', 'badge-success');
            } else if (href.includes('advanced-use-cases')) {
                addResultBadge(result, 'Advanced', 'badge-new');
            }
        }
    });
}

function addResultBadge(result, text, className) {
    if (!result.querySelector('.search-badge')) {
        const badge = document.createElement('span');
        badge.className = `badge ${className} search-badge`;
        badge.textContent = text;
        result.appendChild(badge);
    }
}

// Progress Indicators
function initializeProgressIndicators() {
    // Add progress indicators for multi-step processes
    const stepLists = document.querySelectorAll('ol li');
    stepLists.forEach((item, index, list) => {
        if (list.length > 3) { // Only for lists with more than 3 steps
            addProgressBar(item, index, list.length);
        }
    });
}

function addProgressBar(item, index, total) {
    const progress = document.createElement('div');
    progress.className = 'progress-bar';
    
    const fill = document.createElement('div');
    fill.className = 'progress-fill';
    fill.style.width = `${((index + 1) / total) * 100}%`;
    
    progress.appendChild(fill);
    item.insertBefore(progress, item.firstChild);
}

// Interactive Elements
function initializeInteractiveElements() {
    // Add interactive demos for API calls
    const curlBlocks = document.querySelectorAll('pre code');
    
    curlBlocks.forEach(block => {
        if (block.textContent.includes('curl')) {
            addInteractiveDemo(block);
        }
    });
}

function addInteractiveDemo(codeBlock) {
    const demoContainer = document.createElement('div');
    demoContainer.className = 'interactive-demo';
    
    const title = document.createElement('h4');
    title.textContent = '🔬 Try This API Call';
    
    const button = document.createElement('button');
    button.className = 'demo-button';
    button.textContent = 'Run Example';
    
    const output = document.createElement('div');
    output.className = 'demo-output';
    output.style.display = 'none';
    
    button.addEventListener('click', () => {
        simulateAPICall(output);
    });
    
    demoContainer.appendChild(title);
    demoContainer.appendChild(button);
    demoContainer.appendChild(output);
    
    codeBlock.parentNode.parentNode.insertBefore(demoContainer, codeBlock.parentNode.nextSibling);
}

function simulateAPICall(output) {
    output.style.display = 'block';
    output.innerHTML = '<div class="loading">Executing API call...</div>';
    
    setTimeout(() => {
        output.innerHTML = `
            <div class="json-response">
            <div class="status-indicator status-success"></div>
            <strong>Response: 200 OK</strong>
            <pre><code>{
  "records": [
    {
      "name": "cluster-01",
      "uuid": "12345678-1234-1234-1234-123456789012",
      "state": "up",
      "health": "healthy"
    }
  ],
  "num_records": 1,
  "total_records": 1
}</code></pre>
            </div>
        `;
    }, 1500);
}

// Table Enhancements
function initializeTableEnhancements() {
    const tables = document.querySelectorAll('table');
    
    tables.forEach(table => {
        // Add sortable headers
        addTableSorting(table);
        
        // Add hover effects
        addTableHoverEffects(table);
        
        // Add responsive wrapper
        wrapTableForResponsive(table);
    });
}

function addTableSorting(table) {
    const headers = table.querySelectorAll('th');
    headers.forEach((header, index) => {
        header.style.cursor = 'pointer';
        header.addEventListener('click', () => sortTable(table, index));
    });
}

function sortTable(table, column) {
    const tbody = table.querySelector('tbody');
    if (!tbody) return;
    
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const sortedRows = rows.sort((a, b) => {
        const aText = a.cells[column].textContent.trim();
        const bText = b.cells[column].textContent.trim();
        return aText.localeCompare(bText);
    });
    
    // Clear tbody and append sorted rows
    tbody.innerHTML = '';
    sortedRows.forEach(row => tbody.appendChild(row));
}

function addTableHoverEffects(table) {
    const rows = table.querySelectorAll('tr');
    rows.forEach(row => {
        row.addEventListener('mouseenter', () => {
            row.style.transform = 'scale(1.02)';
            row.style.transition = 'transform 0.2s ease';
        });
        
        row.addEventListener('mouseleave', () => {
            row.style.transform = 'scale(1)';
        });
    });
}

function wrapTableForResponsive(table) {
    if (!table.parentNode.classList.contains('table-responsive')) {
        const wrapper = document.createElement('div');
        wrapper.className = 'table-responsive';
        wrapper.style.overflowX = 'auto';
        
        table.parentNode.insertBefore(wrapper, table);
        wrapper.appendChild(table);
    }
}

// Badge System
function initializeBadges() {
    // Add badges to mark new content, updated sections, etc.
    addContentBadges();
}

function addContentBadges() {
    // Mark advanced use cases as new
    const advancedLinks = document.querySelectorAll('a[href*="advanced-use-cases"]');
    advancedLinks.forEach(link => {
        if (!link.querySelector('.badge')) {
            const badge = document.createElement('span');
            badge.className = 'badge badge-new';
            badge.textContent = 'NEW';
            link.appendChild(badge);
        }
    });
    
    // Mark sequence diagrams as updated
    const diagramHeaders = document.querySelectorAll('h3, h4');
    diagramHeaders.forEach(header => {
        if (header.textContent.includes('Sequence') || header.textContent.includes('Diagram')) {
            const badge = document.createElement('span');
            badge.className = 'badge badge-updated';
            badge.textContent = 'UPDATED';
            header.appendChild(badge);
        }
    });
}

// Scroll Animations
function initializeScrollAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });
    
    // Observe elements for animation
    const elementsToAnimate = document.querySelectorAll('.quick-ref-card, .api-endpoint, .mermaid, .admonition');
    elementsToAnimate.forEach(el => observer.observe(el));
}

// Theme Toggle Enhancements
function initializeThemeToggleEnhancements() {
    const themeToggle = document.querySelector('[data-md-color-scheme]');
    if (themeToggle) {
        // Add smooth transition for theme changes
        document.documentElement.style.transition = 'background-color 0.3s ease, color 0.3s ease';
        
        // Store user preference
        const storedTheme = localStorage.getItem('md-color-scheme');
        if (storedTheme) {
            document.documentElement.setAttribute('data-md-color-scheme', storedTheme);
        }
        
        // Listen for theme changes
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.attributeName === 'data-md-color-scheme') {
                    const newTheme = document.documentElement.getAttribute('data-md-color-scheme');
                    localStorage.setItem('md-color-scheme', newTheme);
                    updateMermaidTheme(newTheme);
                }
            });
        });
        
        observer.observe(document.documentElement, {
            attributes: true,
            attributeFilter: ['data-md-color-scheme']
        });
    }
}

function updateMermaidTheme(theme) {
    // Update Mermaid diagrams theme
    const mermaidElements = document.querySelectorAll('.mermaid');
    mermaidElements.forEach(el => {
        if (window.mermaid) {
            const isDark = theme === 'slate';
            window.mermaid.initialize({
                theme: isDark ? 'dark' : 'default'
            });
        }
    });
}

// Utility Functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Global event listeners
window.addEventListener('load', () => {
    // Initialize any features that need to wait for full load
    initializeAdvancedFeatures();
});

function initializeAdvancedFeatures() {
    // Add keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + K for search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('.md-search__input');
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // Escape to close search
        if (e.key === 'Escape') {
            const searchInput = document.querySelector('.md-search__input');
            if (searchInput && document.activeElement === searchInput) {
                searchInput.blur();
            }
        }
    });
}

// Export functions for external use
window.NetAppDocs = {
    enhanceAPICodeBlock,
    addCopyButton,
    showCopyFeedback,
    simulateAPICall
};
