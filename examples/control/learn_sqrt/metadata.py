from sequrity.control.sqrt import check
from sequrity.control.types.value_with_meta import MetaData, ValueWithMeta

# --8<-- [start:policy_meta_update]
policy_1 = r"""
tool "get_applicant_profile" {
    result {
        @producers |= {"university_database_service"};
        @consumers |= {"admissions_office", "scholarship_committee", "email_service"};
        @tags |= {"education", "university", "personal_data"};
    }
}
"""
# --8<-- [end:policy_meta_update]

check(policy_1)

# --8<-- [start:applicant_profile]
applicant_profile = ValueWithMeta(
    value={"name": "Alice White", "age": 20, "gpa": 3.8},
    meta=MetaData(
        producers={"university_database_service"},
        consumers={"admissions_office", "scholarship_committee", "email_service"},
        tags={"education", "university", "personal_data"},
    ),
)
# --8<-- [end:applicant_profile]

# --8<-- [start:policy_meta_check]
policy_2 = r"""
tool "send_email" {
    hard deny when ("university_database_service" in body.producers) and
        not (to.value in {str like w"*@university.edu", "hr@admission.edu"});
}
"""
# --8<-- [end:policy_meta_check]

check(policy_2)

print("Metadata policy examples parsed successfully.")
