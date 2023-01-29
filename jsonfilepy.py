import json
jsondict = {
    'client': {
        'name': [
            'Igor',
            'Vasilii',
            'Grigori',
        ],
        'telephone': [
            89233211212,
            89233336767,
            89235559090,
        ],
        'tac': [
            '@ifr',
            '@kil',
            '@olf',
        ]
    },
    'unwork': {
        'weekdays': [
            0,
            2,
        ],
        'days': [
            '22.01.2023',
            '17.01.2023',
            '23.01.2023',
            '29.01.2023',
        ],
        'workhours': [
            '08:00',
            '18:00'
        ],
        'dinerhours': [
            '12:00',
            '13:00',
        ]

        },
    # Формат записи словарь, где ключ это дата со словарем, где ключ время начала,
    # значения время окончания, пользоватьель и тип стрижки
    'appoint': {
        '31.01.2023': {
            '08:00': [
                '12:59',
                'user1',
                'compleks'
            ],
            '13:00': [
                '13:59',
                'user2',
                'compleks'
            ],
            '14:00': [
                '13:59',
                'user2',
                'compleks'
            ],
            '15:00': [
                '13:59',
                'user2',
                'compleks'
            ],
            '16:00': [
                '13:59',
                'user2',
                'compleks'
            ],
            '17:00': [
                '13:59',
                'user2',
                'compleks'
            ],
            '18:00': [
                '13:59',
                'user2',
                'compleks'
            ],
        },
    }
}

def jsonwright(dict):
    with open('base.json', 'w') as outfile:
        # jsonString = json.dumps(jsondict, indent=4)
        json.dump(dict, outfile)


def jsonread():
    with open('base.json') as json_file:
        dict = json.load(json_file)

    return dict
jsonwright(jsondict)
