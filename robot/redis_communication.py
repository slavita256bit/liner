import socket


def send_redis_command(command, host='127.0.0.1', port=6379):
    """
    Sends a raw Redis command using the RESP protocol.
    """
    # Connect to Redis
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))

    # Convert the command into RESP format
    command_parts = command.split()
    resp_command = "*{}\r\n".format(len(command_parts))
    for part in command_parts:
        resp_command += "${}\r\n{}\r\n".format(len(part), part)

    # Send the command
    client.sendall(resp_command.encode())

    # Read the response
    response = client.recv(4096).decode()
    client.close()

    return response


def parse_redis_response(response):
    """
    Parses a RESP response and extracts the actual value.
    Supports simple string, bulk string, integer, error, and array responses.
    """
    if not response:
        return None

    def parse_lines(lines, index):
        # Recursive parser for a RESP response starting at the given index.
        prefix = lines[index][0]
        if prefix == '+':  # Simple string
            return lines[index][1:], index + 1
        elif prefix == '$':  # Bulk string
            length = int(lines[index][1:])
            if length == -1:
                return None, index + 1
            return lines[index + 1], index + 2
        elif prefix == ':':  # Integer
            return int(lines[index][1:]), index + 1
        elif prefix == '-':  # Error
            return "Error: " + lines[index][1:], index + 1
        elif prefix == '*':  # Array
            num_elements = int(lines[index][1:])
            index += 1
            result = []
            for _ in range(num_elements):
                element, index = parse_lines(lines, index)
                result.append(element)
            return result, index
        else:
            return "Unknown response type", index + 1

    # Split response into lines (remove empty strings at the end)
    lines = [line for line in response.split("\r\n") if line != '']
    result, _ = parse_lines(lines, 0)
    return result
