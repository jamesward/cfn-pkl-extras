plugins {
    id("com.skillsjars.gradle-plugin") version "0.1.4"
    id("org.pkl-lang") version "0.32.1"
}

pkl {
    project {
        /*
        resolvers {
            register("resolvePklDeps") {
                projectDirectories.from(file("src/"))
            }
        }
         */
        packagers {
            // todo: depend on resolvePklDeps
            register("makePackages") {
                if (version != "unspecified") {
                    environmentVariables.put("VERSION", version.toString())
                }
                projectDirectories.from(file("src/"))
            }
        }
    }

    if (version != "unspecified") {
        pkldocGenerators {
            register("pkldoc") {
                noSymlinks = true
                sourceModules = listOf(uri("package://pkg.pkl-lang.org/github.com/jamesward/cfn-pkl-extras/$version"))
            }
        }
    }
}

tasks.register("clean") {
    description = "Deletes the build directory and other generated files"
    group = "Build"
    doLast {
        delete(layout.buildDirectory)
    }
}

// Agent Skills, extracted with ./gradlew extractSkillsJars
repositories {
    mavenCentral()
}

dependencies {
    skill("com.jamesward:skills:0.0.11")
}

skillsjars {
    outputDir.set(layout.projectDirectory.dir(".kiro/skills"))
}
