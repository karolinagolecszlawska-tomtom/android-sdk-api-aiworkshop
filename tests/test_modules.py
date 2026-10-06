import unittest

from generator import modules

DUO_GRADLE = """\
plugins {
    id(BuildPlugins.COMMON_ANDROID_LIBRARY)
}

val artifactId by extra("map-display-duo-internal")
val groupId by extra("com.tomtom.sdk.maps")
val component by extra(Component.MAP_VIS)

dependencies {
    // Internal
    api(projects.annotations.annotations)
    api(projects.maps.mapDisplayCommon)
    api(projects.maps.mapDisplayStandard)
    implementation(projects.maps.mapDisplayPremium)
    implementation(projects.logging.logger)
    testImplementation(projects.maps.mapTileStore)
}
"""

KMP_GRADLE = """\
val artifactId by extra("routing")
val groupId by extra("com.tomtom.sdk.maps.visualization")

kotlin {
    sourceSets {
        commonMain.dependencies {
            api(projects.maps.visualization.visualization)
            api(projects.maps.mapDisplayStandardBindingInternal)
            implementation(projects.common.commonCore)
        }
    }
}
"""

UNPUBLISHED_GRADLE = """\
plugins {
    id(BuildPlugins.COMMON_ANDROID_LIBRARY)
}
dependencies {
    api(projects.maps.mapDisplayCommon)
}
"""

IN_SCOPE = {
    "maps/map-display-common", "maps/map-display-standard", "maps/map-display-premium",
    "maps/map-tile-store", "maps/visualization/visualization",
    "maps/map-display-standard-binding-internal",
}


class ParseModuleTest(unittest.TestCase):
    def test_coordinate_from_extra_lines(self):
        mod = modules.parse_module("maps/map-display-duo-internal", DUO_GRADLE)
        self.assertEqual(mod["coordinate"], "com.tomtom.sdk.maps:map-display-duo-internal")
        self.assertEqual(mod["module"], "maps/map-display-duo-internal")

    def test_coordinate_uses_group_id_not_directory(self):
        mod = modules.parse_module("maps/visualization/routing", KMP_GRADLE)
        self.assertEqual(mod["coordinate"], "com.tomtom.sdk.maps.visualization:routing")

    def test_module_without_artifact_id_is_skipped(self):
        self.assertIsNone(modules.parse_module("maps/docs", UNPUBLISHED_GRADLE))


class ApiDepsTest(unittest.TestCase):
    def test_top_level_api_deps_found_implementation_ignored_non_maps_dropped(self):
        self.assertEqual(modules.api_deps(DUO_GRADLE, IN_SCOPE),
                         ["maps/map-display-common", "maps/map-display-standard"])

    def test_indented_kmp_source_set_api_deps_found(self):
        self.assertEqual(modules.api_deps(KMP_GRADLE, IN_SCOPE),
                         ["maps/visualization/visualization",
                          "maps/map-display-standard-binding-internal"])

    def test_accessor_camel_case_to_kebab_path(self):
        self.assertEqual(modules.accessor_to_path("maps.mapDisplayCommon"),
                         "maps/map-display-common")
        self.assertEqual(modules.accessor_to_path("maps.visualization.routingCompose"),
                         "maps/visualization/routing-compose")


class ModuleDirsTest(unittest.TestCase):
    def test_directories_under_maps_with_build_file(self):
        tree = [
            "maps/map-display-common/build.gradle.kts",
            "maps/map-display-common/api/state.csv",
            "maps/visualization/routing/build.gradle.kts",
            "maps/docs/README.md",
            "navigation/core/build.gradle.kts",
            "build.gradle.kts",
        ]
        self.assertEqual(modules.module_dirs(tree),
                         ["maps/map-display-common", "maps/visualization/routing"])


if __name__ == "__main__":
    unittest.main()
