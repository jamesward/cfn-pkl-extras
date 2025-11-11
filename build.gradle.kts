plugins {
    id("org.pkl-lang") version "0.30.0"
}

pkl {
    project {
        resolvers {
            register("resolvePklDeps") {
                projectDirectories.from(file("src/"))
            }
        }
        packagers {
            // todo: depend on resolvePklDeps
            register("makePackages") {
                if (version != "unspecified") {
                    environmentVariables.put("VERSION", version.toString())
                }
                projectDirectories.from(file("src/"))
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
}

tasks.register("clean") {
    description = "Deletes the build directory and other generated files"
    group = "Build"
    doLast {
        delete(layout.buildDirectory)
    }
}
