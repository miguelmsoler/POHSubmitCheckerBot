import requests
import json
from types import SimpleNamespace as SN
 
class POHProfileService:

    def __init__(self, profile, update=None, context=None):
        self.profile = profile
        if update:
            self.message = update.message
            self.bot = context.bot

    def process(self):
        r = requests.get('https://api.poh.dev/profiles/' + self.profile)
        response = json.loads(r.text)
        photo_url = response['photo']
        r = requests.get(photo_url)
        self.photo = SN(url=photo_url, data=r.content)
        video_url = response['video']
        r = requests.get(video_url)
        self.video = SN(url=video_url, data=r.content)
        # r = requests.get(get_kleros_video_url)
        # self.video = r.content

if __name__ == "__main__":
    # a test
    # start_url = 'https://app.proofofhumanity.id/profile/0xa4ad70a21f50a6b54d8ba72971e88fe3ee9ad496'
    # profile_id = start_url.rsplit('/',1)[1]

    # get_subgraphs_url = 'https://api.thegraph.com/subgraphs/name/kleros/proof-of-humanity-mainnet'

    # get_subgraphs_body = {
    #                         "id": "voucherQuery",
    #                         "query": "query voucherQuery(\n  $id: ID!\n) {\n  submission(id: $id) {\n    id\n    name\n    requests(orderBy: creationTime, orderDirection: desc, first: 1, where: {registration: true}) {\n      evidence(orderBy: creationTime, first: 1) {\n        URI\n        id\n      }\n      id\n    }\n  }\n}\n",
    #                         "variables": {
    #                             "id": profile_id
    #                         }
    #                     }

    # r = requests.post(url = get_subgraphs_url, data = json.dumps(get_subgraphs_body))
    # response = json.loads(r.text)

    # get_registration_suffix = response['data']['submission']['requests'][0]['evidence'][0]['URI']
    # get_kleros_registration_url = 'https://ipfs.kleros.io/%s' % get_registration_suffix
    
    # r = requests.get(get_kleros_registration_url)
    # response = json.loads(r.text)

    # get_file_suffix = response['fileURI']
    # get_kleros_file_url = 'https://ipfs.kleros.io/%s' % get_file_suffix

    # r = requests.get(get_kleros_file_url)
    # response = json.loads(r.text)

    # get_photo_suffix = response['photo']
    # get_video_suffix = response['video']

    # get_kleros_photo_url = 'https://ipfs.kleros.io/%s' % get_photo_suffix
    # get_kleros_video_url = 'https://ipfs.kleros.io/%s' % get_video_suffix

    # r = requests.get(get_kleros_photo_url)
    # print('saving file %s' % get_photo_suffix.rsplit('/', 1)[-1])
    # with open(get_photo_suffix.rsplit('/', 1)[-1], 'wb') as f:
    #     f.write(r.content)
    # r = requests.get(get_kleros_video_url)
    # print('saving file %s' % get_video_suffix.rsplit('/', 1)[-1])
    # with open(get_video_suffix.rsplit('/', 1)[-1], 'wb') as f:
    #     f.write(r.content)
    poh_service = POHProfileService(profile = '0x4733E1CF43D67Ae4dF0B4CF6Cdbe231b336eF475')
    print(poh_service.profile)
    poh_service.process()
    print(poh_service.photo.url, len(poh_service.photo.data))
    print(poh_service.video.url, len(poh_service.video.data))