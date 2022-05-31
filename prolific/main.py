import prolific


def main():
    config = prolific.get_config()

    study_name = "test"
    study_id = prolific.create_study(config, name=study_name)
    published = prolific.publish_study(config, study_id)
    print(f"Study ID: {study_id} | Status: {'Published' if published else 'Failed to publish'}")

if __name__ == "__main__":
    main()
