// Configuration file for docToolchain
// Auto-created for arc42 documentation
// See https://doctoolchain.org/docToolchain/v3.0.x/015_tasks/03_task_generateSite.html

// Path to the documentation source files
inputPath = 'docs'

// Path where generated output will be stored
outputPath = 'build'

// The main AsciiDoc document that includes all chapters
inputFiles = [
    [file: 'arc42-template.adoc', formats: ['html', 'pdf']],
]

// Microsite configuration for generateSite task
// See https://doctoolchain.org/docToolchain/v2.0.x/015_tasks/03_task_generateSite.html
microsite = [:]

// Confluence configuration (not used, but kept for reference)
confluence = [:]
confluence.with {
    input = [
        [file: "build/html5/arc42-template.html"],
    ]
    ancestorId = ''
    api = 'https://[yourCompany].atlassian.net/wiki/rest/api/'
    spaceKey = ''
    createSubpages = false
    pagePrefix = ''
    preambleTitle = ''
    pageSuffix = ''
    credentials = "${System.getenv('HOME')}/.doctoolchain/credentials-${System.getenv('USER')}.properties"
    extraPageContent = ''
    enableAttachments = false
    attachmentPrefix = ''
    disableMinify = false
    attachmentsOnlyInParent = false
}
