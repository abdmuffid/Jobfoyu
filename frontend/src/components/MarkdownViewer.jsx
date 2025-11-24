import ReactMarkdown from "react-markdown"

const MarkdownViewer = ({ content }) => {
  if (!content) return null

  return (
    <div className="markdown-viewer">
      <ReactMarkdown
        components={{
          h1: (props) => <h1 className="md-h1" {...props} />,
          h2: (props) => <h2 className="md-h2" {...props} />,
          h3: (props) => <h3 className="md-h3" {...props} />,
          p: (props) => <p className="md-p" {...props} />,
          ul: (props) => <ul className="md-list" {...props} />,
          ol: (props) => <ol className="md-list" {...props} />,
          li: (props) => <li className="md-li" {...props} />,
          strong: (props) => <strong className="md-strong" {...props} />,
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}

export default MarkdownViewer
