import telnetlib
import logging


# Set log format
FORMAT = ('%(asctime)-20s %(levelname)-6s %(filename)-8s %(name)-10s '
          '%(funcName)-8s %(message)s')
logging.basicConfig(format=FORMAT)


class VDX:
    def __init__(self, hostname, username, password, loglevel="INFO",
                 telnetdebug=0):
        """
        Represents deveice running VDX.

        :param hostname: IP or FQDN of the device you want to connect to
        :param username: Username
        :param password: Password
        """
        self.hostname = hostname
        self.username = username
        self.password = password
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
        self.prompt = "# "

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
        self.device = telnetlib.Telnet(host=self.hostname, timeout=10)
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


def main():
    pass

if __name__ == "__main__":
    main()
