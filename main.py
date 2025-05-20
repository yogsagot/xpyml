from lib.parser import Parser

if __name__ == "__main__":
    # Test the parser
    test_html = """
    <html>
        <head>
            <title>Test Page</title>
        </head>
        <body class="main" id="content">
            <h1>Hello World</h1>
            <p>This is a <b>test</b> paragraph.</p>
        </body>
    </html>
    """

    parser = Parser()
    result = parser.parse(test_html)
    print(result)