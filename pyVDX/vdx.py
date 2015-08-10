import telnetlib
import logging
from argparse import ArgumentParser


# Set log format
FORMAT = ('%(asctime)-20s %(levelname)-6s %(filename)-8s %(name)-10s '
          '%(funcName)-8s %(message)s')
logging.basicConfig(format=FORMAT)


class VDX:
    def __init__(self, hostname, username, password, timeout=10,
                 loglevel="INFO", telnetdebug=0):
        """
        Represents deveice running VDX.

        :param hostname: IP or FQDN of the device you want to connect to
        :param username: Username
        :param password: Password
        :param timeout: telnet connection timeout
        :param loglevel: logging level
        :param telnetdebug: output telnet debug information level
        """
        self.hostname = hostname
        self.username = username
        self.password = password
        self.timeout = int(timeout)
        # config states
        self.running_config = None
        self.candidate_config = None
        self.original_config = None
        # logger settings
        self.telnetdebug = telnetdebug
        self.log = logging.getLogger(name=self.hostname)
        if loglevel == "INFO":
            self.log.setLevel(logging.INFO)
        elif loglevel == "DEBUG":
            self.log.setLevel(logging.DEBUG)
        else:
            self.log.setLevel(logging.ERROR)
        # console prompt
        self.prompt = '# '

    def __getattr__(self, item):
        def wrapper(*args, **kwargs):
            pipe = kwargs.pop('pipe', None)
            if pipe is None:
                cmd = [item.replace('_', ' ')]
            else:
                cmd = ['{} | {}'.format(item.replace('_', ' '), pipe)]
            return self.run_commands(cmd, **kwargs)[1]

    def open(self):
        """
        Opens the connection with the device
        """
        self.log.debug(("Connect to {hostname} with "
                        "user={username}, password={password}").format(
                       hostname=self.hostname, username=self.username,
                       password=self.password))
        # connection
        self.device = telnetlib.Telnet(host=self.hostname,
                                       timeout=self.timeout)
        # set debuglevel
        self.device.set_debuglevel(self.telnetdebug)
        # login steps
        self.device.read_until(b"login: ")
        self.device.write(self.username.encode('ascii') + b"\n")
        if self.password:
            self.device.read_until(b"Password:")
            self.device.write(self.password.encode('ascii') + b"\n")
        s = self.device.read_until(self.prompt.encode('utf-8'))
        # get valid prompt
        self.prompt = s.decode('utf-8').splitlines()[-1]
        self.log.debug("Prompt = '{}'".format(self.prompt))

    def close(self):
        """
        Closees connection
        """
        self.log.debug("Close connection to {hostname}".format(
                       hostname=self.hostname))
        self.device.close()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def _write(self, string):
        """
        Write string to connection

        :param string: string you want to write
        """
        self.device.write(string.encode('utf-8') + b"\n")

    def _read_until_prompt_after_command(self):
        """
        Read strings until prompt

        Skip first (it must be command) and last line (it must be prompt).
        """
        return (
            "\n".join(
                self._read_until_string(self.prompt).splitlines()[1:-1]
            )
        )

    def _read_until_string(self, string):
        """
        Read strings until given string apper

        :param string: string you want to stop to read from connection
        """
        return self.device.read_until(string.encode('utf-8')).decode('utf-8')

    def read_result(self):
        return self._read_until_prompt_after_command()

    def exec_command(self, command):
        """
        This method will run given commands list.

        :param commands: List of commands you want to run
        :param format: format you want to get; 'native' is no format conversion
        :param timestamps: This will return when each command \
            was executed and how log it took
        """
        try:
            self._write(command.strip() + "\n")
            result = self.read_result()
        except:
            self.log.error("Unexpected error: {}", command)
            raise
        return result


def parse_arguments():
    parser = ArgumentParser()
    # global options
    parser.add_argument("--hostname", required=True)
    parser.add_argument("-u", "--username", required=True)
    parser.add_argument("-p", "--password", required=True)
    parser.add_argument("--timeout", required=False, type=int, default=10)
    parser.add_argument("--loglevel", required=False, default="INFO")
    parser.add_argument("command", default="show version", nargs='*')
    args = parser.parse_args()
    return args


def main(hostname, username, password, timeout, loglevel, command):
    vdx = VDX(hostname=hostname, username=username,
              password=password, timeout=timeout, loglevel=loglevel)
    with vdx:
        result = vdx.exec_command(command)
        vdx.log.info(result)

if __name__ == "__main__":
    args = parse_arguments()
    main(hostname=args.hostname,
         username=args.username,
         password=args.password,
         timeout=args.timeout,
         loglevel=args.loglevel,
         command=" ".join(args.command))
