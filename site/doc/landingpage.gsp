<!-- Landing Page for MCP Documentation Server -->
<!-- Custom styles for better visual appearance -->
<style>
    /* Add spacing between sections */
    .td-box {
        padding-top: 4rem !important;
        padding-bottom: 4rem !important;
    }

    /* Fix hero title spacing from menu and make title larger */
    .td-box--1 {
        padding-top: 8rem !important;
    }
    .td-box--1 .h1 {
        font-size: 3.5rem !important;
        font-weight: 700 !important;
        margin-bottom: 1.5rem !important;
    }

    /* Better code block styling - responsive */
    .td-box pre {
        margin: 1rem 0;
        overflow-x: auto;
        white-space: pre-wrap;
        word-wrap: break-word;
        max-width: 100%;
    }
    .td-box pre code {
        white-space: pre-wrap;
        word-break: break-word;
    }

    /* Card shadows for depth - increased specificity */
    .td-box .card,
    section .card {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
        transition: box-shadow 0.3s ease, transform 0.3s ease;
        border: none !important;
    }
    .td-box .card:hover,
    section .card:hover {
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2) !important;
        transform: translateY(-4px);
    }

    /* Fix Who Benefits section - dark background with light text */
    .td-box--5 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }
    .td-box--5 h2, .td-box--5 h4, .td-box--5 p, .td-box--5 li {
        color: white !important;
    }
    /* Fix white-on-white contrast: make cards semi-transparent to show gradient */
    .td-box--5 .card {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }

    /* Screenshot/demo image styling */
    .demo-screenshot {
        border-radius: 8px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
        max-width: 100%;
        height: auto;
    }
</style>

<section class="row td-box td-box--1 position-relative td-box--gradient td-box--height-auto">
    <div class="container text-center td-arrow-down">
        <span class="h1 mb-4">MCP Documentation Server</span>
        <span class="h3 d-block mt-3">Efficient LLM Interaction with Large Documentation Projects</span>
        <div class="pt-3 lead">
            A Model Context Protocol (MCP) server designed to help Large Language Models navigate and interact
            with complex AsciiDoc and Markdown documentation efficiently.
        </div>

        <!-- Badges -->
        <div class="pt-4 pb-2">
            <img src="https://img.shields.io/github/stars/raifdmueller/asciidoc-mcp?style=social" alt="GitHub stars" class="me-2 mb-2">
            <img src="https://img.shields.io/badge/license-MIT-blue" alt="License MIT" class="me-2 mb-2">
            <img src="https://img.shields.io/badge/coverage-82%25-brightgreen" alt="Coverage 82%" class="me-2 mb-2">
            <img src="https://img.shields.io/badge/python-3.11%2B-blue" alt="Python 3.11+" class="me-2 mb-2">
        </div>

        <div class="pt-4 pb-3">
            <a class="btn btn-lg btn-light me-3 mb-3" href="https://github.com/raifdmueller/asciidoc-mcp">
                <i class="fab fa-github"></i> View on GitHub
            </a>
            <a class="btn btn-lg btn-warning mb-3" href="${content.rootpath}arc42-template.html">
                <i class="fas fa-book"></i> Read Documentation
            </a>
        </div>
    </div>
</section>

<section class="row td-box td-box--2 position-relative td-box--gradient td-box--height-auto">
    <div class="container">
        <div class="row">
            <div class="col-md-12">
                <h2 class="text-center mb-5">Key Features</h2>
            </div>
        </div>
        <div class="row">
            <div class="col-md-4 mb-4">
                <div class="h-100">
                    <h4><i class="fas fa-sitemap text-primary"></i> Hierarchical Navigation</h4>
                    <p>Access document structure without loading entire files. Navigate through chapters, sections, and subsections efficiently.</p>
                </div>
            </div>
            <div class="col-md-4 mb-4">
                <div class="h-100">
                    <h4><i class="fas fa-search text-primary"></i> Content Search</h4>
                    <p>Search across all documentation content with relevance ranking. Find what you need quickly.</p>
                </div>
            </div>
            <div class="col-md-4 mb-4">
                <div class="h-100">
                    <h4><i class="fas fa-link text-primary"></i> Include Resolution</h4>
                    <p>Automatically resolves AsciiDoc include directives. Handles complex multi-file documentation projects.</p>
                </div>
            </div>
        </div>
        <div class="row">
            <div class="col-md-4 mb-4">
                <div class="h-100">
                    <h4><i class="fas fa-edit text-primary"></i> Content Manipulation</h4>
                    <p>Update and insert sections directly via MCP protocol. Atomic writes ensure data integrity.</p>
                </div>
            </div>
            <div class="col-md-4 mb-4">
                <div class="h-100">
                    <h4><i class="fas fa-sync-alt text-primary"></i> File Watching</h4>
                    <p>Automatic updates when files change externally. Always stay synchronized with your documentation.</p>
                </div>
            </div>
            <div class="col-md-4 mb-4">
                <div class="h-100">
                    <h4><i class="fas fa-globe text-primary"></i> Web Interface</h4>
                    <p>Visual document structure browser with auto-launch. Navigate your documentation visually.</p>
                </div>
            </div>
        </div>
    </div>
</section>

<section class="row td-box td-box--3 position-relative td-box--gradient td-box--height-auto">
    <div class="container">
        <div class="row">
            <div class="col-md-12">
                <h2 class="text-center mb-5">Quick Start</h2>
            </div>
        </div>
        <div class="row">
            <div class="col-md-6 mb-4">
                <h4><span class="badge bg-primary">1</span> Install Dependencies</h4>
                <pre class="bg-dark text-light p-3 rounded"><code class="language-bash"># Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt</code></pre>
            </div>
            <div class="col-md-6 mb-4">
                <h4><span class="badge bg-primary">2</span> Configure in Claude Code</h4>
                <p class="small text-muted">Add to <code>~/.claude.json</code>:</p>
                <pre class="bg-dark text-light p-3 rounded"><code class="language-json">{
  "mcpServers": {
    "asciidoc-docs-server": {
      "command": "/path/to/venv/bin/python3",
      "args": ["-m", "src.mcp_server", "/path/to/docs"],
      "env": {
        "ENABLE_WEBSERVER": "true"
      }
    }
  }
}</code></pre>
            </div>
        </div>
        <div class="row mt-4">
            <div class="col-md-12 text-center">
                <p class="lead">That's it! The server will auto-start and open a web interface.</p>
                <a class="btn btn-primary" href="${content.rootpath}arc42-template.html">
                    Read the full documentation →
                </a>
            </div>
        </div>
    </div>
</section>

<section class="row td-box td-box--4 position-relative td-box--gradient td-box--height-auto">
    <div class="container">
        <div class="row">
            <div class="col-md-12">
                <h2 class="text-center mb-5">See It In Action</h2>
            </div>
        </div>
        <div class="row justify-content-center mb-5">
            <div class="col-md-10">
                <div class="card">
                    <div class="card-body text-center p-4">
                        <p class="lead mb-3">
                            <i class="fas fa-globe text-primary me-2"></i>
                            The MCP server includes an optional web interface for visual navigation
                        </p>

                        <!-- Web Interface Screenshot -->
                        <div class="my-4">
                            <img src="${content.rootpath}images/web-interface-preview.png"
                                 alt="MCP Documentation Server Web Interface showing hierarchical document navigation"
                                 class="demo-screenshot">
                        </div>

                        <div class="bg-light p-3 rounded">
                            <p class="mb-2"><strong>Enable with:</strong></p>
                            <code class="text-dark">ENABLE_WEBSERVER=true</code>
                        </div>
                        <p class="text-muted small mt-3">
                            Web interface auto-launches and provides a visual overview of your documentation structure
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>

<section class="row td-box td-box--5 position-relative td-box--gradient td-box--height-auto">
    <div class="container">
        <div class="row">
            <div class="col-md-12">
                <h2 class="text-center mb-5">Who Benefits?</h2>
            </div>
        </div>
        <div class="row">
            <div class="col-md-4 mb-4">
                <div class="card h-100">
                    <div class="card-body">
                        <h4 class="card-title"><i class="fas fa-robot text-primary"></i> AI/LLM Developers</h4>
                        <p class="card-text">
                            Build LLM applications that need to work with large documentation.
                            The MCP protocol provides structured access without token waste.
                        </p>
                        <ul class="small">
                            <li>Token-efficient document access</li>
                            <li>Structured navigation API</li>
                            <li>Ready for Claude Code integration</li>
                        </ul>
                    </div>
                </div>
            </div>
            <div class="col-md-4 mb-4">
                <div class="card h-100">
                    <div class="card-body">
                        <h4 class="card-title"><i class="fas fa-users text-primary"></i> Documentation Teams</h4>
                        <p class="card-text">
                            Manage complex arc42 or multi-file documentation projects with AI assistance.
                            Keep documentation synchronized and accessible.
                        </p>
                        <ul class="small">
                            <li>Auto-refresh on file changes</li>
                            <li>Include resolution for modular docs</li>
                            <li>Visual web interface</li>
                        </ul>
                    </div>
                </div>
            </div>
            <div class="col-md-4 mb-4">
                <div class="card h-100">
                    <div class="card-body">
                        <h4 class="card-title"><i class="fas fa-code text-primary"></i> Software Architects</h4>
                        <p class="card-text">
                            Maintain architecture documentation (arc42, ADRs) with LLM support.
                            Query and update documentation efficiently.
                        </p>
                        <ul class="small">
                            <li>Navigate 600+ page projects</li>
                            <li>Atomic writes ensure integrity</li>
                            <li>Search across all content</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>

<section class="row td-box td-box--6 position-relative td-box--gradient td-box--height-auto">
    <div class="container">
        <div class="row">
            <div class="col-md-12">
                <h2 class="text-center mb-5">Architecture</h2>
            </div>
        </div>
        <div class="row">
            <div class="col-md-12">
                <p class="text-center lead mb-4">
                    Built with a clean, modular architecture following arc42 documentation standards.
                </p>
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <ul class="list-unstyled">
                            <li><i class="fas fa-check-circle text-success"></i> <strong>82% test coverage</strong> (121/123 tests passing)</li>
                            <li><i class="fas fa-check-circle text-success"></i> <strong>Modular design</strong> (7 focused modules, all &lt;500 lines)</li>
                            <li><i class="fas fa-check-circle text-success"></i> <strong>Zero data corruption</strong> (atomic writes with backup strategy)</li>
                        </ul>
                    </div>
                    <div class="col-md-6 mb-3">
                        <ul class="list-unstyled">
                            <li><i class="fas fa-check-circle text-success"></i> <strong>Performance</strong> (&lt;2s startup, &lt;100ms API response)</li>
                            <li><i class="fas fa-check-circle text-success"></i> <strong>Production ready</strong> (v2.0, fully documented)</li>
                            <li><i class="fas fa-check-circle text-success"></i> <strong>Well documented</strong> (complete arc42 + 8 ADRs)</li>
                        </ul>
                    </div>
                </div>
                <div class="text-center mt-4">
                    <a class="btn btn-outline-primary" href="${content.rootpath}arc42/04_solution_strategy.html">
                        Explore the Mental Model →
                    </a>
                </div>
            </div>
        </div>
    </div>
</section>

<section class="row td-box td-box--7 position-relative td-box--gradient td-box--height-auto">
    <div class="container text-center">
        <h2 class="mb-4">Open Source</h2>
        <p class="lead">
            MCP Documentation Server is open source and available on GitHub.
        </p>
        <div class="pt-3">
            <a class="btn btn-lg btn-primary me-3" href="https://github.com/raifdmueller/asciidoc-mcp">
                <i class="fab fa-github"></i> Contribute on GitHub
            </a>
            <a class="btn btn-lg btn-outline-primary" href="https://github.com/raifdmueller/asciidoc-mcp/issues">
                <i class="fas fa-bug"></i> Report Issues
            </a>
        </div>
    </div>
</section>
