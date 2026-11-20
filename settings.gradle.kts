// Google's Maven Central mirror first (fast, no rate limits), then Maven Central
// for anything the mirror doesn't have yet (releases from the last few hours),
// then the Plugin Portal for plugins that are only published there.
pluginManagement {
    repositories {
        maven("https://maven-central.storage-download.googleapis.com/maven2/") { name = "GoogleMavenCentral" }
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolutionManagement {
    repositoriesMode = RepositoriesMode.FAIL_ON_PROJECT_REPOS
    repositories {
        maven("https://maven-central.storage-download.googleapis.com/maven2/") { name = "GoogleMavenCentral" }
        mavenCentral()
    }
}

rootProject.name = "cfn-pkl-extras"
