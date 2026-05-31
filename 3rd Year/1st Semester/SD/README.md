# Shared Key-Value Storage Service

---
## Grade: 16/20 ⭐
---

This project implements a **Shared Key-Value Storage Service**, where data is maintained on a server and accessed remotely by clients via TCP sockets. The system supports concurrent client interactions and multi-threaded operations, making it suitable for scenarios requiring efficient shared data management.

## Features

### Core Functionality
1. **User Authentication and Registration**:
   - Users can register and log in with a username and password.
   - Authentication ensures secure access to the service.

2. **Basic Key-Value Operations**:
   - **Put**: `void put(String key, byte[] value)`
     - Inserts or updates the value for the given key.
   - **Get**: `byte[] get(String key)`
     - Retrieves the value for the given key or `null` if the key does not exist.

3. **Batch Operations**:
   - **MultiPut**: `void multiPut(Map<String, byte[]> pairs)`
     - Inserts or updates multiple key-value pairs atomically.
   - **MultiGet**: `Map<String, byte[]> multiGet(Set<String> keys)`
     - Retrieves multiple key-value pairs for the specified keys.

4. **Concurrent Client Limit**:
   - Configurable server parameter `S` limits the maximum number of concurrent clients.
   - Additional clients are queued until slots are available.

### Advanced Features
1. **Multi-Threaded Clients**:
   - A single client can issue multiple concurrent requests to the server.

2. **Conditional Reads**:
   - **GetWhen**: `byte[] getWhen(String key, String keyCond, byte[] valueCond)`
     - Blocks until the value associated with `keyCond` matches `valueCond`, then retrieves the value for `key`.

3. **Custom Thread Pool**:
   - Efficient thread management using a custom thread pool to handle server requests.

### Performance and Scalability
- Designed to minimize contention and reduce the number of threads unnecessarily awakened.
- Scenarios include varying workloads and increasing numbers of concurrent clients for scalability testing.

---

## Project Structure

### **Server**
The server handles incoming client connections, processes requests, and manages data in memory using a thread-safe key-value store.

Key components:
- **Authentication Service**: Handles user registration and login.
- **Key-Value Store**: Thread-safe in-memory storage for keys and values.
- **Condition Management**: Allows conditional reads using per-key locks and conditions.
- **Custom Thread Pool**: Limits concurrent threads for better scalability.

### **Client Library**
The client library provides an API for interacting with the server. It supports both single-threaded and multi-threaded operations.

Key features:
- **Basic Operations**: `put`, `get`, `multiPut`, `multiGet`.
- **Conditional Reads**: `getWhen` for blocking reads based on conditions.
- **Thread-Safety**: Ensures safe concurrent requests from multiple threads.

### **User Interface**
A simple command-line interface allows testing and interacting with the service.

