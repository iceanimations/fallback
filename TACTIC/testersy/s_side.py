from pyasm.command import Command
from client.tactic_client_lib import TacticServerStub
from app.breakdown.src.backend import _backend as backend
import json
def test():
    return 'abc'

class S_Side(Command):
    def execute(my):
        s = TacticServerStub.get()
        my.info = json.dumps(backend.foo())
