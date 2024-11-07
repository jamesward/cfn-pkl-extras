plugins {
  id("org.pkl-lang") version "0.26.3"
}

val maybeVersion = System.getenv("VERSION")

pkl {
  project {
    packagers {
      register("makePackages") {
        if (maybeVersion != null) {
          environmentVariables.put("VERSION", maybeVersion)
        }
        projectDirectories.from(file("src/"))
      }
    }
  }
  // ./gradlew pkldoc
  if (maybeVersion != null) {
    pkldocGenerators {
      register("pkldoc") {
        sourceModules =
          listOf(uri("package://pkg.pkl-lang.org/github.com/jamesward/cfn-extras/$maybeVersion"))
      }
    }
  }
  tests {
    register("testPkl") {
      sourceModules.add(file("src/patterns_test.pkl"))
      //junitReportsDir.set(layout.buildDirectory.dir("reports"))
      //overwrite.set(false)
    }
  }
}
