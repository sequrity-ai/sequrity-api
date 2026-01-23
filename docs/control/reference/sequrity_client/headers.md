# Configuration Headers

This module contains the configuration header classes used to customize Sequrity's security features, policies, and session behavior.

## Features Header

Configure security features including LLM mode, taggers, and constraints.

::: sequrity_api.types.control.headers.FeaturesHeader
    options:
      show_root_heading: true
      show_source: true
      members_order: source

### LLM Mode Feature

::: sequrity_api.types.control.headers.feature_headers.LlmModeFeature
    options:
      show_root_heading: true
      show_source: false

### Tagger Feature

::: sequrity_api.types.control.headers.feature_headers.TaggerFeature
    options:
      show_root_heading: true
      show_source: false

### Constraint Feature

::: sequrity_api.types.control.headers.feature_headers.ConstraintFeature
    options:
      show_root_heading: true
      show_source: false

---

## Security Policy Header

Configure security policies using sqrt, sqrt-lite, or cedar policy languages.

::: sequrity_api.types.control.headers.SecurityPolicyHeader
    options:
      show_root_heading: true
      show_source: true
      members_order: source

::: sequrity_api.types.control.headers.policy_headers.InternalPolicyPreset
    options:
      show_root_heading: true
      show_source: true

---

## Fine-Grained Config Header

Advanced configuration options for session behavior and response formatting. 💡 Please expand the source to see all available options and descriptions.

::: sequrity_api.types.control.headers.FineGrainedConfigHeader
    options:
      show_root_heading: true
      show_source: true
      members_order: source
