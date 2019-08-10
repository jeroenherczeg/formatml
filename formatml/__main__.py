from formatml.pipelines.pipeline import parse_args


def main() -> None:
    """CLI entry point of the formatml."""
    handler, kw_args, graceful_keyboard_interruption = parse_args()
    handler(**kw_args)
    if graceful_keyboard_interruption:
        try:
            handler(**vars(kw_args))
        except KeyboardInterrupt:
            return
    else:
        handler(**vars(kw_args))


if __name__ == "__main__":
    main()
