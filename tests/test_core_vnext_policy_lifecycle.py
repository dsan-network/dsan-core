import unittest

from dsan.core_vnext import (
    journal_genesis_event,
    journal_genesis_root,
    project_accountable_history,
    sha256_json,
    verify_execution_ledger_records,
)


def build_history(subject, specs):
    previous_event=journal_genesis_event(subject)
    previous_root=journal_genesis_root(subject)
    history=[]
    for sequence,spec in enumerate(specs,start=1):
        event={
            'schema':'dsan:event:1','object_id':spec['event_id'],'object_type':'event','version':1,
            'event_type':spec['event_type'],'subject':subject,'actor':'guardian:alice',
            'timestamp':f'2026-10-01T20:{sequence:02d}:00+00:00','created_at':f'2026-10-01T20:{sequence:02d}:00+00:00',
            'sequence':sequence,'previous_event':previous_event,'causation':[],
            'payload':dict(spec['payload']),'provenance':{'fixture':'policy-lifecycle-v1'},
            'integrity':{'signer':'guardian:alice','key_id':'key:test','algorithm':'Ed25519','signature':'fixture'},
            'authorized':False,
        }
        result=dict(spec['result']);result_root=sha256_json(result)
        material={
            'subject':subject,'sequence':sequence,'previous_event':previous_event,
            'previous_root':previous_root,'event_id':spec['event_id'],'kind':'policy',
            'accepted':True,'event':event,'result':result,'result_root':result_root,
        }
        entry_root=sha256_json(material)
        history.append({**material,'entry_root':entry_root})
        previous_event=spec['event_id'];previous_root=entry_root
    return history


class CoreVNextPolicyLifecycleProjection(unittest.TestCase):
    def test_publish_and_retire_are_state_changes_with_policy_references(self):
        subject='dse:alice'
        specs=[
            {
                'event_id':'event:policy-v2','event_type':'policy.publish',
                'payload':{
                    'policy_id':'policy:record_read_active','version':2,'action':'record.read',
                    'required_context':{'purpose':'care'},'required_lifecycle':'ACTIVE',
                    'effect':'allow','priority':20,'required_conditions':[],
                },
                'result':{
                    'accepted':True,'event_id':'event:policy-v2','subject':subject,
                    'actor':'guardian:alice','operation':'policy.publish','policy_id':'policy:record_read_active',
                    'policy_version':2,'resulting_status':'ACTIVE','reason':'immutable policy version published',
                },
            },
            {
                'event_id':'event:retire-v1','event_type':'policy.retire',
                'payload':{'policy_id':'policy:record_read_active','version':1},
                'result':{
                    'accepted':True,'event_id':'event:retire-v1','subject':subject,
                    'actor':'guardian:alice','operation':'policy.retire','policy_id':'policy:record_read_active',
                    'policy_version':1,'resulting_status':'RETIRED',
                    'reason':'policy version retired without deleting historical material',
                },
            },
        ]
        records=project_accountable_history(subject,build_history(subject,specs))
        self.assertEqual(['STATE_CHANGED','STATE_CHANGED'],[x.event_class for x in records])
        self.assertEqual('policy.publish',records[0].event_type)
        self.assertEqual('policy.retire',records[1].event_type)
        self.assertEqual({'policy_id':'policy:record_read_active','policy_version':2},records[0].references)
        self.assertEqual({'policy_id':'policy:record_read_active','policy_version':1},records[1].references)
        verified=verify_execution_ledger_records(subject,records)
        self.assertTrue(verified.accepted,verified.reason)


if __name__=='__main__':unittest.main()
