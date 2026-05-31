
# Academic Project using MySQL

This is a Java project that uses MySQL as the database, with build and execution configuration through Gradle, made for the class of 'Desenvolvimento de Sistemas de Software' in the 1st semester of the 3rd year of 'Engenharia Informática' at UMinho.

## Requirements

Before compiling and running the project, ensure that the following tools are installed:

- **Java 8 or higher**: The project was developed using Java. Make sure Java is installed on your system.
    - To check if Java is installed, run:
      ```bash
      java -version
      ```

- **MySQL**: Database used to store and manipulate data.
    - Make sure MySQL is installed and running.

## Database Setup

1. **MySQL Setup**:
    - Create a database in MySQL:
      ```sql
      CREATE DATABASE your_database_name;
      ```
    - In the file `src/main/java/SwapDL/Conn`, set the database connection credentials:

      ```properties
      jdbc.url=jdbc:mysql://localhost:3306/your_database_name
      jdbc.username=your_username
      jdbc.password=your_password
      ```

2. **Download MySQL Connector**:
    - The MySQL Connector dependency is automatically managed by Gradle, but if necessary, it can be manually downloaded from [MySQL Connector/J](https://dev.mysql.com/downloads/connector/j/).

## How to Compile and Run

### 1. Clone the Repository

Clone this repository to your local system:

```bash
git clone https://github.com/LEI-DSS/DSS2425-Grupo-34.git
cd DSS2425-Grupo-34
```

### 2. Compile the Project with Gradle

To compile the project, just run the command:

1. **Windows**

```bash
gradle build
```

2. **macOC/Linux**

```bash
./gradlew build
```

This will download all necessary dependencies, compile the source code, and generate the output files.

### 3. Run the Project

After compilation, you can run the application with the command:

1. **Windows**

```bash
gradle run --args="director" //for course director version
```

```bash
gradle run --args="student" //for student version
```

2. **macOC/Linux**

```bash
./gradlew run --args="director" //for course direction version
```

```bash
./gradlew run --args="student" //for student version
```

This will run the main class as a course director or as a student.

## License

This project is licensed under the [MIT License](LICENSE).
