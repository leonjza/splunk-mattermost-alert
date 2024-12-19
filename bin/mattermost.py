import sys

import alert
import log


def is_execution_mode() -> bool:
    """
        Check Splunk execution mode.

        Ref: https://dev.splunk.com/enterprise/docs/devtools/customalertactions/writescriptcaa#About-the-execution-mode

        :return:
    """

    return len(sys.argv) > 1 and sys.argv[1] == '--execute'


if __name__ == '__main__':
    if not is_execution_mode():
        log.error('unsupported execution mode (expected --execute flag)')
        sys.exit(1)

    try:
        processor = alert.Alert()
        processor.send()
        log.info('alert sent successfully')
    except Exception as e:
        log.error('unhandled exception', e)
        sys.exit(1)
