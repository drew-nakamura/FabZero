import json
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import server
from siliconos import ai
from siliconos.engine import DEFAULT, simulate

class ServiceTests(unittest.TestCase):
    def test_ai_response_validation_and_unsupported_intent(self):
        result={'supported':True,'explanation':'Test fixture', 'spec':DEFAULT,
                'provenance':{k:'default' for k in DEFAULT},'unresolved':[]}
        def response(value,finish_reason='stop'):
            return io.BytesIO(json.dumps({'choices':[{'finish_reason':finish_reason,'message':{'role':'assistant','content':json.dumps(value)}}]}).encode())
        with patch.dict('os.environ',{'GROQ_API_KEY':'test-placeholder','GROQ_MODEL':'test-model'}):
            with patch('urllib.request.urlopen',return_value=response(result)):
                self.assertEqual(ai.generate('matrix multiply')['spec'],DEFAULT)
            unsupported={**result,'supported':False,'spec':{**DEFAULT,'operation':'object_detection'}}
            with patch('urllib.request.urlopen',return_value=response(unsupported)):
                self.assertFalse(ai.generate('detect objects')['supported'])
            bad={**result,'spec':{**DEFAULT,'size':128}}
            with patch('urllib.request.urlopen',return_value=response(bad)):
                with self.assertRaises(ValueError): ai.generate('128 square')
            with patch('urllib.request.urlopen',return_value=response(result,'length')):
                with self.assertRaisesRegex(ValueError,'incomplete'): ai.generate('matrix multiply')

    def test_pilot_consent_validation_and_private_persistence(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(server,'DB',Path(folder)/'test.db'):
            payload=dict(email='qa@example.invalid',role='test',platform='test',challenge='test fixture',consent=True)
            with self.assertRaises(ValueError): server.save_pilot({**payload,'consent':False})
            with self.assertRaises(ValueError): server.save_pilot({**payload,'email':'invalid'})
            self.assertEqual(server.save_pilot(payload),{'saved':True})
            server.save_pilot(payload)
            with server.connect() as db:
                self.assertEqual(db.execute('SELECT COUNT(*) FROM pilots').fetchone()[0],1)
                self.assertTrue(json.loads(db.execute('SELECT payload FROM pilots').fetchone()[0])['consent'])

    def test_missing_ai_configuration_never_fakes_spec(self):
        with patch.dict('os.environ',{},clear=True):
            self.assertFalse(ai.configured())
            with self.assertRaisesRegex(ValueError,'not configured'): ai.generate('Make a matrix multiplier')

    def test_bad_simulation_arguments(self):
        for lanes in (True,0,2,16,'4'):
            with self.assertRaises(ValueError): simulate(DEFAULT,lanes)
        with self.assertRaises(ValueError): simulate(DEFAULT,4,seed=-1)

if __name__=='__main__': unittest.main()
