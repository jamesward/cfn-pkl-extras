import org.pkl.gradle.task.EvalTask
import org.pkl.gradle.task.PkldocTask
import org.pkl.gradle.task.ProjectPackageTask
import kotlin.io.path.readText

plugins {
  id("org.pkl-lang") version "0.27.1"
}

val maybeVersion = System.getenv("VERSION")

val fakeModuleCacheDir = layout.buildDirectory.dir("pkl-cache")

pkl {
  evaluators {
    register("evalPackageUri") {
      sourceModules = files(layout.projectDirectory.file("src/PklProject"))
      expression = "package.uri"
      outputFile = layout.buildDirectory.file("pkl/packageUri.txt")
    }
  }
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
  pkldocGenerators {
    register("pkldoc") {
      if (maybeVersion != null) {
        sourceModules = listOf(uri("package://pkg.pkl-lang.org/github.com/jamesward/cfn-pkl-extras/$maybeVersion"))

        // workaround for: https://github.com/apple/pkl/issues/791
        transitiveModules.from(file("foo.txt"))
      }
      else {
        moduleCacheDir = fakeModuleCacheDir
        // workaround for a bug where the import graph analyzer tries to resolve imports of a package
        transitiveModules.from(file("src/PklProject"))
        outputDir = layout.buildDirectory.dir("pkldoc")
      }
    }
  }
  analyzers {
    imports {
      register("patterns") {
        projectDir = file("src/")
        sourceModules.add(file("src/patterns.pkl"))
      }
    }
  }
  tests {
    register("testPkl") {
      projectDir = file("src/")
      sourceModules.add(file("src/patterns_test.pkl"))
    }
  }
}

val evalPackageUri by tasks.existing(EvalTask::class)

if (maybeVersion == null) {
  val pkldoc by tasks.existing(PkldocTask::class) {
    dependsOn(evalPackageUri)
    dependsOn(prepareCacheDir)
    sourceModules.set(evalPackageUri.map { listOf(it.outputs.files.singleFile.toPath().readText()) })
  }
}

val makePackages by tasks.existing(ProjectPackageTask::class)

// Create a cache dir so pkldoc can create documentation without them needing to be published
val prepareCacheDir by tasks.registering(Copy::class) {
  dependsOn(makePackages)
  dependsOn(evalPackageUri)
  from(makePackages.get().outputPath)
  into(fakeModuleCacheDir.map {
    val packageUri = evalPackageUri.get().outputFile.get().asFile.toPath().readText()
    it.dir(packageUri.replace("package://", "package-2/"))
  })
  rename { file ->
    when {
      file.endsWith(".sha256") || file.endsWith(".zip") -> file
      else -> "$file.json"
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
