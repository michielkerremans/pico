def read_page(filename):
    try:
        page = open(filename,'r')
        buffer = page.read()
        page.close()
        return buffer
    except:
        print(filename, " not found.")
        raise FileNotFoundError()

def read_lines(filename):
    buffer = read_page(filename)
    return buffer.split('\r\n')