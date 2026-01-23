# FeaturesHeader, SecurityPolicyHeader, FineGrainedConfigHeader

HTTP headers for configuring Sequrity Control's features, security policies, and fine-grained session settings.


## FeaturesHeader

Configure security features including LLM mode, content taggers, and output constraints.

::: sequrity_api.types.control.headers.FeaturesHeader
    options:
      show_root_heading: true
      show_source: true
      members_order: source

### LlmModeFeature

::: sequrity_api.types.control.headers.feature_headers.LlmModeFeature
    options:
      show_root_heading: true
      show_source: false

### TaggerFeature

::: sequrity_api.types.control.headers.feature_headers.TaggerFeature
    options:
      show_root_heading: true
      show_source: false

### ConstraintFeature

::: sequrity_api.types.control.headers.feature_headers.ConstraintFeature
    options:
      show_root_heading: true
      show_source: false

### LongProgramSupportFeature

::: sequrity_api.types.control.headers.feature_headers.LongProgramSupportFeature
    options:
      show_root_heading: true
      show_source: false

---

## SecurityPolicyHeader

Configure security policies using sqrt, sqrt-lite, or cedar policy languages.

::: sequrity_api.types.control.headers.SecurityPolicyHeader
    options:
      show_root_heading: true
      show_source: true
      members_order: source

### InternalPolicyPreset

::: sequrity_api.types.control.headers.policy_headers.InternalPolicyPreset
    options:
      show_root_heading: true
      show_source: false

### ControlFlowMetaPolicy

::: sequrity_api.types.control.headers.policy_headers.ControlFlowMetaPolicy
    options:
      show_root_heading: true
      show_source: false

---

## FineGrainedConfigHeader

Advanced configuration for session behavior, response formatting, and internal tools.

::: sequrity_api.types.control.headers.FineGrainedConfigHeader
    options:
      show_root_heading: true
      show_source: true
      members_order: source

### ResponseFormat

::: sequrity_api.types.control.headers.session_config_headers.ResponseFormat
    options:
      show_root_heading: true
      show_source: false
