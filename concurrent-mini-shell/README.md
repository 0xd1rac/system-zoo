# Concurrent Mini-Shell

A simple command-line shell implementation in C that supports concurrent command execution, background jobs, signal handling, pipes, and redirection.

## Features

- **Concurrent Command Execution**: Run multiple commands simultaneously
- **Background Job Management**: Execute commands in the background with `&`
- **Job Control**: Manage background processes with `fg`, `bg`, and `jobs` commands
- **Signal Handling**: Proper handling of SIGCHLD, SIGINT, and other signals
- **Thread-Safe Design**: Uses mutexes to protect shared data structures
- **Asynchronous Input Processing**: Dedicated thread for handling user input
- **Pipes**: Connect multiple commands with pipes (`|`)
- **Redirection**: Redirect input/output with `<`, `>`, and `>>`

## Building the Shell

To build the shell, simply run:

```bash
make
```

This will compile the source files and create an executable named `shell`.

To clean the build files:

```bash
make clean
```

## Usage

Run the shell:

```bash
./shell
```

### Supported Commands

- **Regular Commands**: Any command available in your system PATH
  ```
  shell> ls
  shell> ps
  shell> echo "Hello, World!"
  ```

- **Background Execution**: Append `&` to run a command in the background
  ```
  shell> sleep 10 &
  [1] 1234 sleep
  ```

- **Pipes**: Connect multiple commands with pipes
  ```
  shell> ls | grep .txt
  shell> cat file.txt | wc -l
  shell> ps aux | grep bash
  ```

- **Redirection**: Redirect input and output
  ```
  shell> ls > files.txt
  shell> cat < input.txt
  shell> echo "Hello" >> output.txt
  ```

- **Combined Features**: Use pipes and redirection together
  ```
  shell> cat input.txt | grep "pattern" > output.txt
  shell> ls | sort > sorted_files.txt &
  [1] 1234 ls
  ```

- **Built-in Commands**:
  - `jobs`: List all background jobs
    ```
    shell> jobs
    [1] Running sleep
    [2] Running top
    ```
  
  - `fg <job_id>`: Bring a background job to the foreground
    ```
    shell> fg 1
    # Waits for the job to complete
    ```
  
  - `bg <job_id>`: Continue a stopped job in the background
    ```
    shell> bg 1
    ```
  
  - `exit`: Exit the shell
    ```
    shell> exit
    ```

## Implementation Details

### Architecture

The shell is implemented using a multi-threaded architecture:

1. **Main Thread**: Initializes the shell, sets up signal handlers, and manages the overall shell state
2. **Input Handler Thread**: Continuously reads and processes user input
3. **Job Monitor Thread**: Periodically checks the status of background jobs

### Key Components

- **Job Control**: Maintains a linked list of background jobs with their status
- **Signal Handling**: Properly handles SIGCHLD for child process termination and SIGINT for Ctrl-C
- **Command Parsing**: Parses command lines into arguments and detects background execution
- **Process Management**: Uses fork() and exec() for command execution
- **Pipeline Execution**: Creates pipes between processes and manages file descriptors
- **Redirection**: Handles input/output redirection with file operations

### Data Structures

- **Job Structure**: Tracks process ID, job ID, command, and status
- **Job List**: Linked list implementation for managing multiple jobs
- **Shell State**: Global state containing job list and synchronization primitives
- **Command Structure**: Parses and stores command arguments and redirection information
- **Pipeline Structure**: Manages multiple commands connected by pipes

## Limitations

- No command history
- No tab completion
- No environment variable expansion
- Limited error handling for complex pipelines

## Future Improvements

- Implement command history with up/down arrow navigation
- Add tab completion for commands and files
- Support environment variable expansion
- Add more built-in commands (cd, pwd, etc.)
- Improve error handling for complex pipelines

## License

This project is open source and available under the MIT License. 