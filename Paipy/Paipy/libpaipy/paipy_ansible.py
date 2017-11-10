#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ansible
from ansible.playbook import PlayBook
from ansible.inventory import Inventory
from ansible import callbacks
from ansible import utils
import sys
import json

class PaipyAnsible:

    def deploy(self, playbook_file, ansible_host, private_key):

        self.playbook_file = playbook_file
        self.ansible_host = ansible_host
        self.private_key = private_key

        stats = callbacks.AggregateStats()
        playbook_cb = callbacks.PlaybookCallbacks(verbose=utils.VERBOSITY)
        inventory = ansible.inventory.Inventory(ansible_host)
        runner_cb = callbacks.PlaybookRunnerCallbacks(stats,verbose=utils.VERBOSITY)

        pb = ansible.playbook.PlayBook(playbook=playbook_file,
        callbacks=playbook_cb,
        runner_callbacks=runner_cb,
        stats=stats,
        inventory=inventory,
        private_key_file=self.private_key)

        out = pb.run()
        print type(out)
        #print('coco %s ' % out['failures'])
        #print out['pai-test1.net']['failures']
        i = json.dumps(out, sort_keys=True, indent=4, separators=(',', ': '))
        print type(i)
        #print i[self.ansible_host]
        #print i['failures']
        #print out['failures']
        #print i
        #logger.info('queue %s exist')
        #if out['failures'] > 0

#def main():
#	my_obj = ExecutePlaybook()
#	my_obj.deploy(playbook_file, ansible_host, private_key)
#
#if __name__ == '__main__':
#    sys.exit(main())
