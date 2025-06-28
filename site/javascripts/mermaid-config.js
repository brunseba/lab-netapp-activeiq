/**
 * Mermaid Configuration for NetApp ActiveIQ MCP Server Documentation
 * This script initializes Mermaid with theme support and responsive diagrams
 */

document.addEventListener('DOMContentLoaded', function() {
  // Check if Mermaid is loaded
  if (typeof mermaid !== 'undefined') {
    
    // Get current theme
    const palette = JSON.parse(localStorage.getItem('__palette') || '{"index": 0}');
    const isDark = palette.index === 1;
    
    // Mermaid configuration
    const config = {
      startOnLoad: true,
      theme: isDark ? 'dark' : 'default',
      themeVariables: {
        // Primary colors for NetApp branding
        primaryColor: '#2196f3',
        primaryTextColor: isDark ? '#ffffff' : '#000000',
        primaryBorderColor: '#1976d2',
        lineColor: isDark ? '#888888' : '#666666',
        
        // Secondary colors
        secondaryColor: '#ff9800',
        tertiaryColor: '#4caf50',
        
        // Background colors
        background: isDark ? '#1e1e1e' : '#ffffff',
        mainBkg: isDark ? '#2d2d2d' : '#f9f9f9',
        secondBkg: isDark ? '#3d3d3d' : '#f0f0f0',
        
        // Text colors
        textColor: isDark ? '#ffffff' : '#000000',
        darkTextColor: isDark ? '#cccccc' : '#333333',
        
        // Node styling
        nodeBkg: isDark ? '#3d3d3d' : '#ffffff',
        nodeBorder: '#2196f3',
        clusterBkg: isDark ? '#2d2d2d' : '#f5f5f5',
        clusterBorder: '#cccccc',
        
        // Edge styling
        edgeLabelBackground: isDark ? '#2d2d2d' : '#ffffff',
        
        // Activity diagram
        actorBkg: isDark ? '#4a4a4a' : '#ffffff',
        actorBorder: '#2196f3',
        actorTextColor: isDark ? '#ffffff' : '#000000',
        actorLineColor: '#2196f3',
        signalColor: isDark ? '#ffffff' : '#000000',
        signalTextColor: isDark ? '#ffffff' : '#000000',
        labelBoxBkgColor: isDark ? '#3d3d3d' : '#ffffff',
        labelBoxBorderColor: '#cccccc',
        labelTextColor: isDark ? '#ffffff' : '#000000',
        loopTextColor: isDark ? '#ffffff' : '#000000',
        noteBorderColor: '#ff9800',
        noteBkgColor: isDark ? '#4a3d2a' : '#fff3cd',
        noteTextColor: isDark ? '#ffffff' : '#000000',
        
        // Sequence diagram
        activationBorderColor: '#2196f3',
        activationBkgColor: isDark ? '#3d4a5a' : '#e3f2fd',
        sequenceNumberColor: isDark ? '#ffffff' : '#000000',
        
        // State diagram
        labelColor: isDark ? '#ffffff' : '#000000',
        
        // Class diagram
        classText: isDark ? '#ffffff' : '#000000',
        
        // Git graph
        git0: '#2196f3',
        git1: '#4caf50',
        git2: '#ff9800',
        git3: '#f44336',
        git4: '#9c27b0',
        git5: '#00bcd4',
        git6: '#795548',
        git7: '#607d8b',
        gitBranchLabel0: isDark ? '#ffffff' : '#000000',
        gitBranchLabel1: isDark ? '#ffffff' : '#000000',
        gitBranchLabel2: isDark ? '#ffffff' : '#000000',
        gitBranchLabel3: isDark ? '#ffffff' : '#000000',
        gitBranchLabel4: isDark ? '#ffffff' : '#000000',
        gitBranchLabel5: isDark ? '#ffffff' : '#000000',
        gitBranchLabel6: isDark ? '#ffffff' : '#000000',
        gitBranchLabel7: isDark ? '#ffffff' : '#000000',
        
        // Pie chart
        pie1: '#2196f3',
        pie2: '#4caf50',
        pie3: '#ff9800',
        pie4: '#f44336',
        pie5: '#9c27b0',
        pie6: '#00bcd4',
        pie7: '#795548',
        pie8: '#607d8b',
        pie9: '#ffc107',
        pie10: '#e91e63',
        pie11: '#673ab7',
        pie12: '#009688',
        pieTitleTextSize: '25px',
        pieTitleTextColor: isDark ? '#ffffff' : '#000000',
        pieSectionTextSize: '17px',
        pieSectionTextColor: isDark ? '#ffffff' : '#000000',
        pieLegendTextSize: '17px',
        pieLegendTextColor: isDark ? '#ffffff' : '#000000',
        pieStrokeColor: isDark ? '#333333' : '#ffffff',
        pieStrokeWidth: '2px',
        pieOpacity: '0.7'
      },
      
      // Flowchart configuration
      flowchart: {
        htmlLabels: true,
        curve: 'linear',
        padding: 15,
        nodeSpacing: 50,
        rankSpacing: 50,
        diagramPadding: 8,
        useMaxWidth: true
      },
      
      // Sequence diagram configuration
      sequence: {
        actorMargin: 50,
        boxMargin: 10,
        boxTextMargin: 5,
        noteMargin: 10,
        messageMargin: 35,
        mirrorActors: true,
        bottomMarginAdj: 1,
        useMaxWidth: true,
        rightAngles: false,
        showSequenceNumbers: false,
        diagramMarginX: 50,
        diagramMarginY: 10,
        actorFontSize: 14,
        actorFontFamily: '"Open Sans", sans-serif',
        actorFontWeight: 400,
        noteFontSize: 14,
        noteFontFamily: '"trebuchet ms", verdana, arial, sans-serif',
        noteFontWeight: 400,
        noteAlign: 'center',
        messageFontSize: 16,
        messageFontFamily: '"trebuchet ms", verdana, arial, sans-serif',
        messageFontWeight: 400,
        wrap: false,
        wrapPadding: 10,
        labelBoxWidth: 50,
        labelBoxHeight: 20
      },
      
      // Gantt configuration
      gantt: {
        titleTopMargin: 25,
        barHeight: 20,
        fontSie: 11,
        sidePadding: 75,
        gridLineStartPadding: 35,
        fontSize: 11,
        fontFamily: '"Open Sans", sans-serif',
        numberSectionStyles: 4,
        axisFormat: '%Y-%m-%d',
        tickInterval: '1day',
        useMaxWidth: true
      },
      
      // Class diagram configuration
      class: {
        arrowMarkerAbsolute: false,
        useMaxWidth: true
      },
      
      // State diagram configuration
      state: {
        dividerMargin: 10,
        sizeUnit: 5,
        confKeys: [
          'diagramPadding',
          'titleTopMargin',
          'subGraphTitleMargin'
        ]
      },
      
      // Journey diagram configuration
      journey: {
        diagramMarginX: 50,
        diagramMarginY: 10,
        actorMargin: 50,
        width: 150,
        height: 65,
        boxMargin: 10,
        boxTextMargin: 5,
        noteMargin: 10,
        messageMargin: 35,
        messageAlign: 'center',
        bottomMarginAdj: 1,
        useMaxWidth: true,
        rightAngles: false
      },
      
      // Git graph configuration
      gitGraph: {
        diagramPadding: 8,
        nodeLabel: {
          width: 75,
          height: 100,
          x: -25,
          y: 0
        }
      },
      
      // Security settings
      securityLevel: 'loose',
      
      // Error handling
      suppressErrorRendering: false,
      
      // Log level
      logLevel: 'error'
    };
    
    // Initialize Mermaid
    mermaid.initialize(config);
    
    // Function to re-render diagrams when theme changes
    function updateMermaidTheme() {
      const newPalette = JSON.parse(localStorage.getItem('__palette') || '{"index": 0}');
      const newIsDark = newPalette.index === 1;
      
      if (newIsDark !== isDark) {
        // Update theme and re-initialize
        config.theme = newIsDark ? 'dark' : 'default';
        config.themeVariables.primaryTextColor = newIsDark ? '#ffffff' : '#000000';
        config.themeVariables.textColor = newIsDark ? '#ffffff' : '#000000';
        config.themeVariables.background = newIsDark ? '#1e1e1e' : '#ffffff';
        config.themeVariables.mainBkg = newIsDark ? '#2d2d2d' : '#f9f9f9';
        config.themeVariables.lineColor = newIsDark ? '#888888' : '#666666';
        
        mermaid.initialize(config);
        
        // Re-render all Mermaid diagrams
        const diagrams = document.querySelectorAll('.mermaid');
        diagrams.forEach((diagram, index) => {
          const graphDefinition = diagram.textContent || diagram.innerText;
          const graphId = `mermaid-${index}`;
          diagram.innerHTML = '';
          diagram.id = graphId;
          
          mermaid.render(graphId, graphDefinition).then(result => {
            diagram.innerHTML = result.svg;
          }).catch(error => {
            console.error('Mermaid rendering error:', error);
            diagram.innerHTML = `<div class="mermaid-error">Error rendering diagram: ${error.message}</div>`;
          });
        });
      }
    }
    
    // Listen for theme changes
    const observer = new MutationObserver(function(mutations) {
      mutations.forEach(function(mutation) {
        if (mutation.type === 'attributes' && mutation.attributeName === 'data-md-color-scheme') {
          setTimeout(updateMermaidTheme, 100);
        }
      });
    });
    
    // Start observing theme changes
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['data-md-color-scheme']
    });
    
    // Handle responsive diagrams
    function makeResponsive() {
      const diagrams = document.querySelectorAll('.mermaid svg');
      diagrams.forEach(svg => {
        const width = svg.getAttribute('width');
        const height = svg.getAttribute('height');
        
        if (width && height) {
          svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
          svg.setAttribute('width', '100%');
          svg.setAttribute('height', 'auto');
          svg.style.maxWidth = '100%';
          svg.style.height = 'auto';
        }
      });
    }
    
    // Make diagrams responsive after page load
    setTimeout(makeResponsive, 500);
    
    // Also make responsive on window resize
    window.addEventListener('resize', makeResponsive);
    
    console.log('Mermaid configuration loaded successfully');
  } else {
    console.warn('Mermaid library not found');
  }
});

// CSS injection for better diagram styling
const style = document.createElement('style');
style.textContent = `
  .mermaid {
    text-align: center;
    margin: 1em 0;
  }
  
  .mermaid svg {
    max-width: 100%;
    height: auto;
  }
  
  .mermaid-error {
    background-color: #ffebee;
    border: 1px solid #f44336;
    border-radius: 4px;
    padding: 1em;
    margin: 1em 0;
    color: #c62828;
    font-family: 'Roboto Mono', monospace;
    font-size: 0.9em;
  }
  
  [data-md-color-scheme="slate"] .mermaid-error {
    background-color: #3e2723;
    border-color: #ff5722;
    color: #ff8a65;
  }
  
  /* Improve diagram readability */
  .mermaid .node rect,
  .mermaid .node circle,
  .mermaid .node ellipse,
  .mermaid .node polygon {
    stroke-width: 2px;
  }
  
  .mermaid .edgePath .path {
    stroke-width: 2px;
  }
  
  .mermaid .edgeLabel {
    background-color: var(--md-default-bg-color);
    padding: 2px 4px;
    border-radius: 2px;
  }
  
  /* Sequence diagrams */
  .mermaid .actor {
    font-weight: 500;
  }
  
  .mermaid .messageText {
    font-weight: 400;
  }
  
  /* Responsive breakpoints */
  @media (max-width: 768px) {
    .mermaid {
      font-size: 12px;
    }
  }
  
  @media (max-width: 480px) {
    .mermaid {
      font-size: 10px;
    }
  }
`;

document.head.appendChild(style);
