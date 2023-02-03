import subprocess
from attrs import define
from .renderer import Renderer


class StableDiffusionRenderer(Renderer):
    def __attrs_post_init__(self):
        self.invoke_ai = InvokeAiProcess(self.config)

    def run(self, instructions: list[dict]) -> list[str]:
        # TODO: Process input instructions to match InvokeAI generate_from_prompts
        pass


@define
class InvokeAiProcess:
    config: dict

    def __attrs_post_init__(self):
        print("Starting Invoke AI...")
        cmd = f"{self.config['stable_diffusion']['venv_path']} {self.config['stable_diffusion']['script_path']} --root_dir {self.config['stable_diffusion']['sd_root']} -o {self.config['stable_diffusion']['save_dir']} --model {self.config['stable_diffusion']['model']} -W 512 -H 512"

        self.__process = subprocess.Popen(
            cmd,
            shell=False,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

        self.__wait_for_stdout("* Initialization done! Awaiting your command (-h for help, 'q' to quit)")

    def generate_from_prompt(self, input_prompt: str):
        print(f"Generating image from prompt: [{input_prompt}]...")
        self.__process.stdin.write(f'{input_prompt}\n'.encode('utf-8'))
        self.__process.stdin.write("\r\n".encode('utf-8'))  # emulate "ENTER" in thread
        self.__process.stdin.flush()

        self.__wait_for_stdout('')

    def __wait_for_stdout(self, wait_for: str):
        print(f"Waiting for stdout output: [{wait_for}]\n")

        while True:
            line = self.__process.stdout.readline()
            print(line)
            if line == f'{wait_for}\r\n'.encode('utf-8'): break

        print("Ready!")
