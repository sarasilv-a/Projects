plugins {
    id("java")
    id("application")
    id("com.github.johnrengelman.shadow") version "7.1.2"
}

val main = "sd.client.ClientInterface"

application {
    mainClass.set(main)
}

tasks.withType<Jar> {
    manifest {
        attributes["Main-Class"] = main
    }
}

repositories {
    mavenCentral()
}

dependencies {
    implementation("org.jetbrains:annotations:24.0.0")
    testImplementation(platform("org.junit:junit-bom:5.9.1"))
    testImplementation("org.junit.jupiter:junit-jupiter")
    implementation(project(":common"))
    implementation("org.jline:jline-reader:3.24.0")
    implementation("org.jline:jline-terminal:3.24.0")
    implementation("org.jline:jline-terminal-jansi:3.24.0")
    implementation ("com.fasterxml.jackson.core:jackson-databind:2.14.0")
    implementation ("com.fasterxml.jackson.core:jackson-core:2.14.0")
    implementation ("com.fasterxml.jackson.core:jackson-annotations:2.14.0")
}

tasks.test {
    useJUnitPlatform()
}

tasks.build {
    dependsOn("shadowJar")
}