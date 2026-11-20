pluginManagement {
    repositories {
        // the plugins and their dependencies are published to Maven Central; the
        // Plugin Portal only redirects there, and a failed redirect fails the build
        mavenCentral()
        gradlePluginPortal()
    }
}

rootProject.name = "cfn-pkl-extras"
