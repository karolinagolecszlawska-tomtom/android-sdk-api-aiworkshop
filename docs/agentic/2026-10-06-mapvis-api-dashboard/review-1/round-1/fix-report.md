## Covering tests

- Defect 1 (tests/test_acceptance.py: acceptance setUp fails when out/ is missing): `tests/test_acceptance.py` — `CleanCheckoutTest.test_acceptance_skips_when_outputs_missing` (points DATA/HTML at a missing out/ and asserts an AcceptanceTest is skipped with the run hint, no failures or errors). Also checked by hand: with out/ moved away, `python3 -m unittest discover -s tests` gives `Ran 89 tests ... OK (skipped=14)`.

## Command

`time python3 -m generator --out out --extra-catalog old-version=fixtures/old-version.versions.toml && python3 -m unittest discover -s tests -v`

## Output

```
wrote out/data.json, out/dashboard.html, 21 state.csv files under out/raw/

real	0m13.734s
user	0m3.320s
sys	0m2.106s
test_m1_artifact_direct_consumers_match_reference (test_acceptance.AcceptanceTest.test_m1_artifact_direct_consumers_match_reference) ... ok
test_m1_direct_pairs_match_reference (test_acceptance.AcceptanceTest.test_m1_direct_pairs_match_reference) ... ok
test_m2_docs_repos_only_in_docs_references (test_acceptance.AcceptanceTest.test_m2_docs_repos_only_in_docs_references) ... ok
test_m3_jpn_kor_styles_have_zero_direct_consumers (test_acceptance.AcceptanceTest.test_m3_jpn_kor_styles_have_zero_direct_consumers) ... ok
test_m4_baselines (test_acceptance.AcceptanceTest.test_m4_baselines) ... ok
test_m4_no_negative_counts_and_html_shows_both_baselines (test_acceptance.AcceptanceTest.test_m4_no_negative_counts_and_html_shows_both_baselines) ... ok
test_m4_old_version_fixture (test_acceptance.AcceptanceTest.test_m4_old_version_fixture) ... ok
test_m4_real_consumers_zero_behind_rc_and_ahead_of_stable (test_acceptance.AcceptanceTest.test_m4_real_consumers_zero_behind_rc_and_ahead_of_stable) ... ok
test_m5_outputs_contain_no_api_key (test_acceptance.AcceptanceTest.test_m5_outputs_contain_no_api_key) ... ok
test_s1_r2_navapp_transitive_via_duo_internal (test_acceptance.AcceptanceTest.test_s1_r2_navapp_transitive_via_duo_internal) ... ok
test_s1_transitive_never_duplicates_direct (test_acceptance.AcceptanceTest.test_s1_transitive_never_duplicates_direct) ... ok
test_s3_unconsumed_artifacts_and_packages_listed (test_acceptance.AcceptanceTest.test_s3_unconsumed_artifacts_and_packages_listed) ... ok
test_s4_internal_availability_column_and_total (test_acceptance.AcceptanceTest.test_s4_internal_availability_column_and_total) ... ok
test_s5_consumed_visualization_modules_state_unknown (test_acceptance.AcceptanceTest.test_s5_consumed_visualization_modules_state_unknown) ... ok
test_acceptance_skips_when_outputs_missing (test_acceptance.CleanCheckoutTest.test_acceptance_skips_when_outputs_missing) ... ok
test_m5_injected_key_is_obfuscated (test_acceptance.InjectedKeyTest.test_m5_injected_key_is_obfuscated) ... wrote /var/folders/9j/jnc1xbcx23792qm3y90108mh0000gn/T/tmpagd8mah5/out/data.json, /var/folders/9j/jnc1xbcx23792qm3y90108mh0000gn/T/tmpagd8mah5/out/dashboard.html, 1 state.csv files under /var/folders/9j/jnc1xbcx23792qm3y90108mh0000gn/T/tmpagd8mah5/out/raw/
ok
test_m5_output_stage_redacts_model (test_acceptance.InjectedKeyTest.test_m5_output_stage_redacts_model)
A key that reaches the model unredacted is still obfuscated in both outputs. ... wrote /var/folders/9j/jnc1xbcx23792qm3y90108mh0000gn/T/tmpdioumw7i/out/data.json, /var/folders/9j/jnc1xbcx23792qm3y90108mh0000gn/T/tmpdioumw7i/out/dashboard.html, 0 state.csv files under /var/folders/9j/jnc1xbcx23792qm3y90108mh0000gn/T/tmpdioumw7i/out/raw/
ok
test_artifacts_are_published_in_scope_modules (test_build.AssembleTest.test_artifacts_are_published_in_scope_modules) ... ok
test_baselines_and_consumer_versions (test_build.AssembleTest.test_baselines_and_consumer_versions) ... ok
test_catalog_without_mapvis_libraries_fails_loudly (test_build.AssembleTest.test_catalog_without_mapvis_libraries_fails_loudly) ... ok
test_direct_pairs_from_catalogs_deduped (test_build.AssembleTest.test_direct_pairs_from_catalogs_deduped) ... ok
test_docs_references_fixed_and_never_consumers (test_build.AssembleTest.test_docs_references_fixed_and_never_consumers) ... ok
test_extra_catalogs_kept_out_of_direct_pairs (test_build.AssembleTest.test_extra_catalogs_kept_out_of_direct_pairs) ... ok
test_in_scope_modules_from_codeowners_and_tree (test_build.AssembleTest.test_in_scope_modules_from_codeowners_and_tree) ... ok
test_model_is_json_serialisable (test_build.AssembleTest.test_model_is_json_serialisable) ... ok
test_published_modules_skip_unpublished (test_build.AssembleTest.test_published_modules_skip_unpublished) ... ok
test_stability_and_state_totals (test_build.AssembleTest.test_stability_and_state_totals) ... ok
test_totals_count_direct_and_transitive (test_build.AssembleTest.test_totals_count_direct_and_transitive) ... ok
test_transitive_does_not_duplicate_direct (test_build.AssembleTest.test_transitive_does_not_duplicate_direct) ... ok
test_transitive_one_level_via_artifact (test_build.AssembleTest.test_transitive_one_level_via_artifact) ... ok
test_unconsumed_artifacts_and_packages (test_build.AssembleTest.test_unconsumed_artifacts_and_packages) ... ok
test_unpublished_module_state_csv_not_fetched_nor_counted (test_build.CollectTest.test_unpublished_module_state_csv_not_fetched_nor_counted) ... ok
test_every_call_is_get_only (test_build.GithubTest.test_every_call_is_get_only) ... ok
test_raw_error_merely_containing_404_raises (test_build.GithubTest.test_raw_error_merely_containing_404_raises) ... ok
test_raw_is_redacted (test_build.GithubTest.test_raw_is_redacted) ... ok
test_raw_missing_file_returns_none (test_build.GithubTest.test_raw_missing_file_returns_none) ... ok
test_raw_other_error_raises (test_build.GithubTest.test_raw_other_error_raises) ... ok
test_consumer_catalog_files_are_fixed (test_catalogs.CatalogTest.test_consumer_catalog_files_are_fixed) ... ok
test_fixture_resolves_gosdk_for_two_maps_libraries (test_catalogs.CatalogTest.test_fixture_resolves_gosdk_for_two_maps_libraries) ... ok
test_no_space_inline_table_and_literal_version (test_catalogs.CatalogTest.test_no_space_inline_table_and_literal_version) ... ok
test_non_maps_groups_dropped_and_aliases_deduped (test_catalogs.CatalogTest.test_non_maps_groups_dropped_and_aliases_deduped) ... ok
test_pinned_version_is_lowest_resolved (test_catalogs.CatalogTest.test_pinned_version_is_lowest_resolved) ... ok
test_commented_lines_and_trailing_comments_ignored (test_codeowners.CodeownersTest.test_commented_lines_and_trailing_comments_ignored) ... ok
test_double_star_globs_do_not_match_the_module_directory_itself (test_codeowners.CodeownersTest.test_double_star_globs_do_not_match_the_module_directory_itself) ... ok
test_in_scope_when_any_team_pattern_matches (test_codeowners.CodeownersTest.test_in_scope_when_any_team_pattern_matches) ... ok
test_last_match_wins_for_visualization_routing (test_codeowners.CodeownersTest.test_last_match_wins_for_visualization_routing) ... ok
test_more_specific_later_rule_overrides (test_codeowners.CodeownersTest.test_more_specific_later_rule_overrides) ... ok
test_multiple_owners_are_all_reported (test_codeowners.CodeownersTest.test_multiple_owners_are_all_reported) ... ok
test_team_paths_lists_patterns_naming_the_team (test_codeowners.CodeownersTest.test_team_paths_lists_patterns_naming_the_team) ... ok
test_unanchored_glob_matches_anywhere (test_codeowners.CodeownersTest.test_unanchored_glob_matches_anywhere) ... ok
test_unowned_path (test_codeowners.CodeownersTest.test_unowned_path) ... ok
test_consumer_versions_section (test_html.RenderTest.test_consumer_versions_section) ... ok
test_docs_references_section_lists_both_repos (test_html.RenderTest.test_docs_references_section_lists_both_repos) ... ok
test_empty_state_csv_is_not_state_unknown (test_html.RenderTest.test_empty_state_csv_is_not_state_unknown) ... ok
test_extra_catalogs_section_when_present (test_html.RenderTest.test_extra_catalogs_section_when_present) ... ok
test_grouped_by_package (test_html.RenderTest.test_grouped_by_package) ... ok
test_no_consumers_section (test_html.RenderTest.test_no_consumers_section) ... ok
test_no_key_in_output (test_html.RenderTest.test_no_key_in_output) ... ok
test_self_contained_document (test_html.RenderTest.test_self_contained_document) ... ok
test_stability_totals_one_column_per_state (test_html.RenderTest.test_stability_totals_one_column_per_state) ... ok
test_state_columns_include_internal_availability (test_html.RenderTest.test_state_columns_include_internal_availability) ... ok
test_state_unknown_shown (test_html.RenderTest.test_state_unknown_shown) ... ok
test_text_is_escaped (test_html.RenderTest.test_text_is_escaped) ... ok
test_transitive_consumer_shown_via_artifact (test_html.RenderTest.test_transitive_consumer_shown_via_artifact) ... ok
test_accessor_camel_case_to_kebab_path (test_modules.ApiDepsTest.test_accessor_camel_case_to_kebab_path) ... ok
test_indented_kmp_source_set_api_deps_found (test_modules.ApiDepsTest.test_indented_kmp_source_set_api_deps_found) ... ok
test_top_level_api_deps_found_implementation_ignored_non_maps_dropped (test_modules.ApiDepsTest.test_top_level_api_deps_found_implementation_ignored_non_maps_dropped) ... ok
test_directories_under_maps_with_build_file (test_modules.ModuleDirsTest.test_directories_under_maps_with_build_file) ... ok
test_coordinate_from_extra_lines (test_modules.ParseModuleTest.test_coordinate_from_extra_lines) ... ok
test_coordinate_uses_group_id_not_directory (test_modules.ParseModuleTest.test_coordinate_uses_group_id_not_directory) ... ok
test_module_without_artifact_id_is_skipped (test_modules.ParseModuleTest.test_module_without_artifact_id_is_skipped) ... ok
test_every_occurrence_obfuscated (test_redact.RedactTest.test_every_occurrence_obfuscated) ... ok
test_key_in_url_keeps_surrounding_text (test_redact.RedactTest.test_key_in_url_keeps_surrounding_text) ... ok
test_key_token_obfuscated (test_redact.RedactTest.test_key_token_obfuscated) ... ok
test_short_values_left_alone (test_redact.RedactTest.test_short_values_left_alone) ... ok
test_class_and_member_rows (test_state.PackageOfTest.test_class_and_member_rows) ... ok
test_file_facade_row (test_state.PackageOfTest.test_file_facade_row) ... ok
test_lowercase_inside_parentheses_ignored (test_state.PackageOfTest.test_lowercase_inside_parentheses_ignored) ... ok
test_semicolon_split_keeps_commas_in_names (test_state.ParseRowsTest.test_semicolon_split_keeps_commas_in_names) ... ok
test_missing_state_csv_is_state_unknown (test_state.TallyTest.test_missing_state_csv_is_state_unknown) ... ok
test_module_with_state_csv (test_state.TallyTest.test_module_with_state_csv) ... ok
test_tally_per_package_and_state_with_internal_availability_separate (test_state.TallyTest.test_tally_per_package_and_state_with_internal_availability_separate) ... ok
test_old_version_fixture_is_12_behind_latest_rc (test_versions.BehindTest.test_old_version_fixture_is_12_behind_latest_rc) ... ok
test_older_pin_counts_tags_up_to_baseline (test_versions.BehindTest.test_older_pin_counts_tags_up_to_baseline) ... ok
test_pin_equal_to_baseline_is_zero (test_versions.BehindTest.test_pin_equal_to_baseline_is_zero) ... ok
test_pin_newer_than_stable_is_ahead (test_versions.BehindTest.test_pin_newer_than_stable_is_ahead) ... ok
test_drops_drafts_and_dev_tags (test_versions.ReleaseTagsTest.test_drops_drafts_and_dev_tags) ... ok
test_latest_rc_is_highest_semver_rc (test_versions.ReleaseTagsTest.test_latest_rc_is_highest_semver_rc) ... ok
test_rc_sorts_before_stable_of_same_version (test_versions.ReleaseTagsTest.test_rc_sorts_before_stable_of_same_version) ... ok

----------------------------------------------------------------------
Ran 89 tests in 0.031s

OK
```
