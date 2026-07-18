import json

template_node_group: dict = json.loads("""{
                            "name": "template_effect.002",
                            "nodes": [
                                {
                                    "type": "NodeGroupOutput",
                                    "name": "Group Output",
                                    "label": "",
                                    "props": {
                                        "display_in_effect": false,
                                        "display_order": 0,
                                        "location": [
                                            -123.06559753417969,
                                            190.1424560546875
                                        ],
                                        "select": false
                                    },
                                    "inputs": [
                                        [
                                            "Output_2",
                                            "visualizer",
                                            "Output_3"
                                        ],
                                        [
                                            "Output_3",
                                            "visualizer",
                                            "Output_4"
                                        ]
                                    ]
                                },
                                {
                                    "type": "NodeGroupInput",
                                    "name": "Group Input",
                                    "label": "",
                                    "props": {
                                        "display_in_effect": false,
                                        "display_order": 0,
                                        "location": [
                                            -1171.4544677734375,
                                            116.84744262695312
                                        ],
                                        "select": false
                                    }
                                },
                                {
                                    "type": "GeometryNodeGroup",
                                    "name": "visualizer",
                                    "label": "visualizer",
                                    "node_group": {
                                        "name": "visualizer.003",
                                        "nodes": [
                                            {
                                                "type": "FunctionNodeCompare",
                                                "name": "Compare",
                                                "label": "",
                                                "props": {
                                                    "display_in_effect": false,
                                                    "display_order": 0,
                                                    "data_type": "STRING",
                                                    "location": [
                                                        -688.9213256835938,
                                                        189.47364807128906
                                                    ],
                                                    "operation": "EQUAL",
                                                    "select": false,
                                                    "width": 162.71368408203125
                                                },
                                                "inputs": [
                                                    [
                                                        "A",
                                                        0.0
                                                    ],
                                                    [
                                                        "B",
                                                        0.0
                                                    ],
                                                    [
                                                        "A_INT",
                                                        0
                                                    ],
                                                    [
                                                        "B_INT",
                                                        0
                                                    ],
                                                    [
                                                        "A_VEC3",
                                                        [
                                                            0.0,
                                                            0.0,
                                                            0.0
                                                        ]
                                                    ],
                                                    [
                                                        "B_VEC3",
                                                        [
                                                            0.0,
                                                            0.0,
                                                            0.0
                                                        ]
                                                    ],
                                                    [
                                                        "A_COL",
                                                        [
                                                            0.0,
                                                            0.0,
                                                            0.0,
                                                            0.0
                                                        ]
                                                    ],
                                                    [
                                                        "B_COL",
                                                        [
                                                            0.0,
                                                            0.0,
                                                            0.0,
                                                            0.0
                                                        ]
                                                    ],
                                                    [
                                                        "A_STR",
                                                        "distribution"
                                                    ],
                                                    [
                                                        "B_STR",
                                                        "channel",
                                                        "String"
                                                    ],
                                                    [
                                                        "C",
                                                        0.8999999761581421
                                                    ],
                                                    [
                                                        "Angle",
                                                        0.08726649731397629
                                                    ],
                                                    [
                                                        "Epsilon",
                                                        0.0010000000474974513
                                                    ]
                                                ]
                                            },
                                            {
                                                "type": "GeometryNodeSwitch",
                                                "name": "Switch.001",
                                                "label": "",
                                                "props": {
                                                    "display_in_effect": false,
                                                    "display_order": 0,
                                                    "input_type": "STRING",
                                                    "location": [
                                                        -485.8096923828125,
                                                        230.68548583984375
                                                    ],
                                                    "select": false,
                                                    "width": 144.9859619140625
                                                },
                                                "inputs": [
                                                    [
                                                        "Switch",
                                                        "Compare",
                                                        "Result"
                                                    ],
                                                    [
                                                        "Switch_001",
                                                        false
                                                    ],
                                                    [
                                                        "False",
                                                        0.0
                                                    ],
                                                    [
                                                        "True",
                                                        0.0
                                                    ],
                                                    [
                                                        "False_001",
                                                        0
                                                    ],
                                                    [
                                                        "True_001",
                                                        0
                                                    ],
                                                    [
                                                        "False_002",
                                                        false
                                                    ],
                                                    [
                                                        "True_002",
                                                        true
                                                    ],
                                                    [
                                                        "False_003",
                                                        [
                                                            0.0,
                                                            0.0,
                                                            0.0
                                                        ]
                                                    ],
                                                    [
                                                        "True_003",
                                                        [
                                                            0.0,
                                                            0.0,
                                                            0.0
                                                        ]
                                                    ],
                                                    [
                                                        "False_004",
                                                        [
                                                            0.800000011920929,
                                                            0.800000011920929,
                                                            0.800000011920929,
                                                            1.0
                                                        ]
                                                    ],
                                                    [
                                                        "True_004",
                                                        [
                                                            0.800000011920929,
                                                            0.800000011920929,
                                                            0.800000011920929,
                                                            1.0
                                                        ]
                                                    ],
                                                    [
                                                        "False_005",
                                                        "scale_visualizer"
                                                    ],
                                                    [
                                                        "True_005",
                                                        "distribution_visualizer"
                                                    ],
                                                    [
                                                        "False_006",
                                                        null
                                                    ],
                                                    [
                                                        "True_006",
                                                        null
                                                    ],
                                                    [
                                                        "False_007",
                                                        null
                                                    ],
                                                    [
                                                        "True_007",
                                                        null
                                                    ],
                                                    [
                                                        "False_008",
                                                        null
                                                    ],
                                                    [
                                                        "True_008",
                                                        null
                                                    ],
                                                    [
                                                        "False_009",
                                                        null
                                                    ],
                                                    [
                                                        "True_009",
                                                        null
                                                    ],
                                                    [
                                                        "False_010",
                                                        null
                                                    ],
                                                    [
                                                        "True_010",
                                                        null
                                                    ],
                                                    [
                                                        "False_011",
                                                        null
                                                    ],
                                                    [
                                                        "True_011",
                                                        null
                                                    ]
                                                ]
                                            },
                                            {
                                                "type": "FunctionNodeInputString",
                                                "name": "channel",
                                                "label": "",
                                                "props": {
                                                    "display_in_effect": false,
                                                    "display_order": 0,
                                                    "location": [
                                                        -852.371826171875,
                                                        -343.7497253417969
                                                    ],
                                                    "select": false
                                                }
                                            },
                                            {
                                                "type": "GeometryNodeInputNamedAttribute",
                                                "name": "Node.001",
                                                "label": "",
                                                "props": {
                                                    "display_in_effect": false,
                                                    "display_order": 0,
                                                    "location": [
                                                        -320.0,
                                                        -320.0
                                                    ],
                                                    "select": false
                                                },
                                                "inputs": [
                                                    [
                                                        "Name",
                                                        "channel",
                                                        "String"
                                                    ]
                                                ]
                                            },
                                            {
                                                "type": "NodeReroute",
                                                "name": "Reroute",
                                                "label": "",
                                                "props": {
                                                    "display_in_effect": false,
                                                    "display_order": 0,
                                                    "location": [
                                                        -328.0591125488281,
                                                        -464.1612243652344
                                                    ],
                                                    "select": false,
                                                    "width": 16.0
                                                },
                                                "inputs": [
                                                    [
                                                        "Input",
                                                        "Group Input",
                                                        "Data"
                                                    ]
                                                ]
                                            },
                                            {
                                                "type": "GeometryNodeInputNamedAttribute",
                                                "name": "Named Attribute.001",
                                                "label": "",
                                                "props": {
                                                    "display_in_effect": false,
                                                    "display_order": 0,
                                                    "location": [
                                                        -245.82366943359375,
                                                        224.08572387695312
                                                    ],
                                                    "select": false
                                                },
                                                "inputs": [
                                                    [
                                                        "Name",
                                                        "Switch.001",
                                                        "Output_005"
                                                    ]
                                                ]
                                            },
                                            {
                                                "type": "NodeGroupInput",
                                                "name": "Group Input",
                                                "label": "",
                                                "props": {
                                                    "display_in_effect": false,
                                                    "display_order": 0,
                                                    "location": [
                                                        -861.7876586914062,
                                                        3.138645648956299
                                                    ],
                                                    "select": false
                                                }
                                            },
                                            {
                                                "type": "GeometryNodeGroup",
                                                "name": "mixer",
                                                "label": "",
                                                "node_group": {
                                                    "name": "mixer.022",
                                                    "nodes": [
                                                        {
                                                            "type": "ShaderNodeMixRGB",
                                                            "name": "mixer.002",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "blend_type": "MULTIPLY",
                                                                "location": [
                                                                    20.0,
                                                                    40.0
                                                                ],
                                                                "select": false
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "Fac",
                                                                    "Group Input",
                                                                    "_influence"
                                                                ],
                                                                [
                                                                    "Color1",
                                                                    "Reroute",
                                                                    "Output"
                                                                ],
                                                                [
                                                                    "Color2",
                                                                    "Reroute.001",
                                                                    "Output"
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "GeometryNodeSwitch",
                                                            "name": "Switch.002",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "input_type": "RGBA",
                                                                "location": [
                                                                    20.0,
                                                                    220.0
                                                                ],
                                                                "select": false
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "Switch",
                                                                    "Compare.002",
                                                                    "Result"
                                                                ],
                                                                [
                                                                    "Switch_001",
                                                                    false
                                                                ],
                                                                [
                                                                    "False",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "True",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "False_001",
                                                                    0
                                                                ],
                                                                [
                                                                    "True_001",
                                                                    0
                                                                ],
                                                                [
                                                                    "False_002",
                                                                    false
                                                                ],
                                                                [
                                                                    "True_002",
                                                                    true
                                                                ],
                                                                [
                                                                    "False_003",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "True_003",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "False_004",
                                                                    "Switch.003",
                                                                    "Output_004"
                                                                ],
                                                                [
                                                                    "True_004",
                                                                    "mixer.002",
                                                                    "Color"
                                                                ],
                                                                [
                                                                    "False_005",
                                                                    ""
                                                                ],
                                                                [
                                                                    "True_005",
                                                                    ""
                                                                ],
                                                                [
                                                                    "False_006",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_006",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_007",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_007",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_008",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_008",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_009",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_009",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_010",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_010",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_011",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_011",
                                                                    null
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "FunctionNodeCompare",
                                                            "name": "Compare.002",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "data_type": "STRING",
                                                                "location": [
                                                                    20.0,
                                                                    400.0
                                                                ],
                                                                "operation": "EQUAL",
                                                                "select": false
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "A",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "B",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "A_INT",
                                                                    0
                                                                ],
                                                                [
                                                                    "B_INT",
                                                                    0
                                                                ],
                                                                [
                                                                    "A_VEC3",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "B_VEC3",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "A_COL",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "B_COL",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "A_STR",
                                                                    "Group Input",
                                                                    "_blend_type"
                                                                ],
                                                                [
                                                                    "B_STR",
                                                                    "MULTIPLY"
                                                                ],
                                                                [
                                                                    "C",
                                                                    0.8999999761581421
                                                                ],
                                                                [
                                                                    "Angle",
                                                                    0.08726649731397629
                                                                ],
                                                                [
                                                                    "Epsilon",
                                                                    0.0010000000474974513
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "GeometryNodeSwitch",
                                                            "name": "Switch.003",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "input_type": "RGBA",
                                                                "location": [
                                                                    -220.0,
                                                                    220.0
                                                                ],
                                                                "select": false
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "Switch",
                                                                    "Compare.003",
                                                                    "Result"
                                                                ],
                                                                [
                                                                    "Switch_001",
                                                                    false
                                                                ],
                                                                [
                                                                    "False",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "True",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "False_001",
                                                                    0
                                                                ],
                                                                [
                                                                    "True_001",
                                                                    0
                                                                ],
                                                                [
                                                                    "False_002",
                                                                    false
                                                                ],
                                                                [
                                                                    "True_002",
                                                                    true
                                                                ],
                                                                [
                                                                    "False_003",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "True_003",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "False_004",
                                                                    "Switch.004",
                                                                    "Output_004"
                                                                ],
                                                                [
                                                                    "True_004",
                                                                    "mixer.003",
                                                                    "Color"
                                                                ],
                                                                [
                                                                    "False_005",
                                                                    ""
                                                                ],
                                                                [
                                                                    "True_005",
                                                                    ""
                                                                ],
                                                                [
                                                                    "False_006",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_006",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_007",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_007",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_008",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_008",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_009",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_009",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_010",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_010",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_011",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_011",
                                                                    null
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "ShaderNodeMixRGB",
                                                            "name": "mixer.003",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "blend_type": "ADD",
                                                                "location": [
                                                                    -220.0,
                                                                    40.0
                                                                ],
                                                                "select": false
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "Fac",
                                                                    "Group Input",
                                                                    "_influence"
                                                                ],
                                                                [
                                                                    "Color1",
                                                                    "Reroute",
                                                                    "Output"
                                                                ],
                                                                [
                                                                    "Color2",
                                                                    "Reroute.001",
                                                                    "Output"
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "FunctionNodeCompare",
                                                            "name": "Compare.003",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "data_type": "STRING",
                                                                "location": [
                                                                    -220.0,
                                                                    400.0
                                                                ],
                                                                "operation": "EQUAL",
                                                                "select": false
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "A",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "B",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "A_INT",
                                                                    0
                                                                ],
                                                                [
                                                                    "B_INT",
                                                                    0
                                                                ],
                                                                [
                                                                    "A_VEC3",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "B_VEC3",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "A_COL",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "B_COL",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "A_STR",
                                                                    "Group Input",
                                                                    "_blend_type"
                                                                ],
                                                                [
                                                                    "B_STR",
                                                                    "ADD"
                                                                ],
                                                                [
                                                                    "C",
                                                                    0.8999999761581421
                                                                ],
                                                                [
                                                                    "Angle",
                                                                    0.08726649731397629
                                                                ],
                                                                [
                                                                    "Epsilon",
                                                                    0.0010000000474974513
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "GeometryNodeSwitch",
                                                            "name": "Switch.004",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "input_type": "RGBA",
                                                                "location": [
                                                                    -460.0,
                                                                    220.0
                                                                ],
                                                                "select": false
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "Switch",
                                                                    "Compare.004",
                                                                    "Result"
                                                                ],
                                                                [
                                                                    "Switch_001",
                                                                    false
                                                                ],
                                                                [
                                                                    "False",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "True",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "False_001",
                                                                    0
                                                                ],
                                                                [
                                                                    "True_001",
                                                                    0
                                                                ],
                                                                [
                                                                    "False_002",
                                                                    false
                                                                ],
                                                                [
                                                                    "True_002",
                                                                    true
                                                                ],
                                                                [
                                                                    "False_003",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "True_003",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "False_004",
                                                                    "Switch.005",
                                                                    "Output_004"
                                                                ],
                                                                [
                                                                    "True_004",
                                                                    "mixer.004",
                                                                    "Color"
                                                                ],
                                                                [
                                                                    "False_005",
                                                                    ""
                                                                ],
                                                                [
                                                                    "True_005",
                                                                    ""
                                                                ],
                                                                [
                                                                    "False_006",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_006",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_007",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_007",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_008",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_008",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_009",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_009",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_010",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_010",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_011",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_011",
                                                                    null
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "ShaderNodeMixRGB",
                                                            "name": "mixer.004",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "blend_type": "DIVIDE",
                                                                "location": [
                                                                    -460.0,
                                                                    40.0
                                                                ],
                                                                "select": false
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "Fac",
                                                                    "Group Input",
                                                                    "_influence"
                                                                ],
                                                                [
                                                                    "Color1",
                                                                    "Reroute",
                                                                    "Output"
                                                                ],
                                                                [
                                                                    "Color2",
                                                                    "Reroute.001",
                                                                    "Output"
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "FunctionNodeCompare",
                                                            "name": "Compare.004",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "data_type": "STRING",
                                                                "location": [
                                                                    -460.0,
                                                                    400.0
                                                                ],
                                                                "operation": "EQUAL",
                                                                "select": false
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "A",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "B",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "A_INT",
                                                                    0
                                                                ],
                                                                [
                                                                    "B_INT",
                                                                    0
                                                                ],
                                                                [
                                                                    "A_VEC3",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "B_VEC3",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "A_COL",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "B_COL",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "A_STR",
                                                                    "Group Input",
                                                                    "_blend_type"
                                                                ],
                                                                [
                                                                    "B_STR",
                                                                    "DIVIDE"
                                                                ],
                                                                [
                                                                    "C",
                                                                    0.8999999761581421
                                                                ],
                                                                [
                                                                    "Angle",
                                                                    0.08726649731397629
                                                                ],
                                                                [
                                                                    "Epsilon",
                                                                    0.0010000000474974513
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "ShaderNodeMixRGB",
                                                            "name": "mixer.001",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "blend_type": "DARKEN",
                                                                "location": [
                                                                    260.0,
                                                                    40.0
                                                                ],
                                                                "select": false
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "Fac",
                                                                    "Group Input",
                                                                    "_influence"
                                                                ],
                                                                [
                                                                    "Color1",
                                                                    "Reroute.001",
                                                                    "Output"
                                                                ],
                                                                [
                                                                    "Color2",
                                                                    "Reroute",
                                                                    "Output"
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "GeometryNodeSwitch",
                                                            "name": "Switch.001",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "input_type": "RGBA",
                                                                "location": [
                                                                    260.0,
                                                                    220.0
                                                                ],
                                                                "select": false
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "Switch",
                                                                    "Compare.001",
                                                                    "Result"
                                                                ],
                                                                [
                                                                    "Switch_001",
                                                                    false
                                                                ],
                                                                [
                                                                    "False",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "True",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "False_001",
                                                                    0
                                                                ],
                                                                [
                                                                    "True_001",
                                                                    0
                                                                ],
                                                                [
                                                                    "False_002",
                                                                    false
                                                                ],
                                                                [
                                                                    "True_002",
                                                                    true
                                                                ],
                                                                [
                                                                    "False_003",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "True_003",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "False_004",
                                                                    "Switch.002",
                                                                    "Output_004"
                                                                ],
                                                                [
                                                                    "True_004",
                                                                    "mixer.001",
                                                                    "Color"
                                                                ],
                                                                [
                                                                    "False_005",
                                                                    ""
                                                                ],
                                                                [
                                                                    "True_005",
                                                                    ""
                                                                ],
                                                                [
                                                                    "False_006",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_006",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_007",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_007",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_008",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_008",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_009",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_009",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_010",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_010",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_011",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_011",
                                                                    null
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "FunctionNodeCompare",
                                                            "name": "Compare",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "data_type": "STRING",
                                                                "location": [
                                                                    500.0,
                                                                    400.0
                                                                ],
                                                                "operation": "EQUAL",
                                                                "select": false
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "A",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "B",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "A_INT",
                                                                    0
                                                                ],
                                                                [
                                                                    "B_INT",
                                                                    0
                                                                ],
                                                                [
                                                                    "A_VEC3",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "B_VEC3",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "A_COL",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "B_COL",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "A_STR",
                                                                    "Group Input",
                                                                    "_blend_type"
                                                                ],
                                                                [
                                                                    "B_STR",
                                                                    "MIX"
                                                                ],
                                                                [
                                                                    "C",
                                                                    0.8999999761581421
                                                                ],
                                                                [
                                                                    "Angle",
                                                                    0.08726649731397629
                                                                ],
                                                                [
                                                                    "Epsilon",
                                                                    0.0010000000474974513
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "ShaderNodeMixRGB",
                                                            "name": "mixer",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "location": [
                                                                    500.0,
                                                                    40.0
                                                                ],
                                                                "select": false
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "Fac",
                                                                    "Group Input",
                                                                    "_influence"
                                                                ],
                                                                [
                                                                    "Color1",
                                                                    "Reroute",
                                                                    "Output"
                                                                ],
                                                                [
                                                                    "Color2",
                                                                    "Reroute.001",
                                                                    "Output"
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "FunctionNodeCompare",
                                                            "name": "Compare.001",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "data_type": "STRING",
                                                                "location": [
                                                                    260.0,
                                                                    400.0
                                                                ],
                                                                "operation": "EQUAL",
                                                                "select": false
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "A",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "B",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "A_INT",
                                                                    0
                                                                ],
                                                                [
                                                                    "B_INT",
                                                                    0
                                                                ],
                                                                [
                                                                    "A_VEC3",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "B_VEC3",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "A_COL",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "B_COL",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "A_STR",
                                                                    "Group Input",
                                                                    "_blend_type"
                                                                ],
                                                                [
                                                                    "B_STR",
                                                                    "DARKEN"
                                                                ],
                                                                [
                                                                    "C",
                                                                    0.8999999761581421
                                                                ],
                                                                [
                                                                    "Angle",
                                                                    0.08726649731397629
                                                                ],
                                                                [
                                                                    "Epsilon",
                                                                    0.0010000000474974513
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "ShaderNodeMixRGB",
                                                            "name": "mixer.005",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "blend_type": "SUBTRACT",
                                                                "location": [
                                                                    -700.0,
                                                                    40.0
                                                                ],
                                                                "select": false
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "Fac",
                                                                    "Group Input",
                                                                    "_influence"
                                                                ],
                                                                [
                                                                    "Color1",
                                                                    "Reroute",
                                                                    "Output"
                                                                ],
                                                                [
                                                                    "Color2",
                                                                    "Reroute.001",
                                                                    "Output"
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "FunctionNodeCompare",
                                                            "name": "Compare.005",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "data_type": "STRING",
                                                                "location": [
                                                                    -700.0,
                                                                    400.0
                                                                ],
                                                                "operation": "EQUAL",
                                                                "select": false
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "A",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "B",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "A_INT",
                                                                    0
                                                                ],
                                                                [
                                                                    "B_INT",
                                                                    0
                                                                ],
                                                                [
                                                                    "A_VEC3",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "B_VEC3",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "A_COL",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "B_COL",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "A_STR",
                                                                    "Group Input",
                                                                    "_blend_type"
                                                                ],
                                                                [
                                                                    "B_STR",
                                                                    "SUBTRACT"
                                                                ],
                                                                [
                                                                    "C",
                                                                    0.8999999761581421
                                                                ],
                                                                [
                                                                    "Angle",
                                                                    0.08726649731397629
                                                                ],
                                                                [
                                                                    "Epsilon",
                                                                    0.0010000000474974513
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "GeometryNodeSwitch",
                                                            "name": "Switch.005",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "input_type": "RGBA",
                                                                "location": [
                                                                    -700.0,
                                                                    220.0
                                                                ],
                                                                "select": false
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "Switch",
                                                                    "Compare.005",
                                                                    "Result"
                                                                ],
                                                                [
                                                                    "Switch_001",
                                                                    false
                                                                ],
                                                                [
                                                                    "False",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "True",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "False_001",
                                                                    0
                                                                ],
                                                                [
                                                                    "True_001",
                                                                    0
                                                                ],
                                                                [
                                                                    "False_002",
                                                                    false
                                                                ],
                                                                [
                                                                    "True_002",
                                                                    true
                                                                ],
                                                                [
                                                                    "False_003",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "True_003",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "False_004",
                                                                    "Switch.006",
                                                                    "Output_004"
                                                                ],
                                                                [
                                                                    "True_004",
                                                                    "mixer.005",
                                                                    "Color"
                                                                ],
                                                                [
                                                                    "False_005",
                                                                    ""
                                                                ],
                                                                [
                                                                    "True_005",
                                                                    ""
                                                                ],
                                                                [
                                                                    "False_006",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_006",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_007",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_007",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_008",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_008",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_009",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_009",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_010",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_010",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_011",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_011",
                                                                    null
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "FunctionNodeCompare",
                                                            "name": "Compare.006",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "data_type": "STRING",
                                                                "location": [
                                                                    -960.0,
                                                                    400.0
                                                                ],
                                                                "operation": "EQUAL",
                                                                "select": false
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "A",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "B",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "A_INT",
                                                                    0
                                                                ],
                                                                [
                                                                    "B_INT",
                                                                    0
                                                                ],
                                                                [
                                                                    "A_VEC3",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "B_VEC3",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "A_COL",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "B_COL",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "A_STR",
                                                                    "Group Input",
                                                                    "_blend_type"
                                                                ],
                                                                [
                                                                    "B_STR",
                                                                    "DIFFERENCE"
                                                                ],
                                                                [
                                                                    "C",
                                                                    0.8999999761581421
                                                                ],
                                                                [
                                                                    "Angle",
                                                                    0.08726649731397629
                                                                ],
                                                                [
                                                                    "Epsilon",
                                                                    0.0010000000474974513
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "GeometryNodeSwitch",
                                                            "name": "Switch.006",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "input_type": "RGBA",
                                                                "location": [
                                                                    -960.0,
                                                                    220.0
                                                                ],
                                                                "select": false
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "Switch",
                                                                    "Compare.006",
                                                                    "Result"
                                                                ],
                                                                [
                                                                    "Switch_001",
                                                                    false
                                                                ],
                                                                [
                                                                    "False",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "True",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "False_001",
                                                                    0
                                                                ],
                                                                [
                                                                    "True_001",
                                                                    0
                                                                ],
                                                                [
                                                                    "False_002",
                                                                    false
                                                                ],
                                                                [
                                                                    "True_002",
                                                                    true
                                                                ],
                                                                [
                                                                    "False_003",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "True_003",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "False_004",
                                                                    "mixer.007",
                                                                    "Color"
                                                                ],
                                                                [
                                                                    "True_004",
                                                                    "mixer.006",
                                                                    "Color"
                                                                ],
                                                                [
                                                                    "False_005",
                                                                    ""
                                                                ],
                                                                [
                                                                    "True_005",
                                                                    ""
                                                                ],
                                                                [
                                                                    "False_006",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_006",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_007",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_007",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_008",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_008",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_009",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_009",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_010",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_010",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_011",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_011",
                                                                    null
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "ShaderNodeMixRGB",
                                                            "name": "mixer.006",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "blend_type": "DIFFERENCE",
                                                                "location": [
                                                                    -960.0,
                                                                    40.0
                                                                ],
                                                                "select": false
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "Fac",
                                                                    "Group Input",
                                                                    "_influence"
                                                                ],
                                                                [
                                                                    "Color1",
                                                                    "Reroute",
                                                                    "Output"
                                                                ],
                                                                [
                                                                    "Color2",
                                                                    "Reroute.001",
                                                                    "Output"
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "ShaderNodeMixRGB",
                                                            "name": "mixer.007",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "location": [
                                                                    -1200.0,
                                                                    160.0
                                                                ],
                                                                "select": false
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "Fac",
                                                                    "Group Input",
                                                                    "_influence"
                                                                ],
                                                                [
                                                                    "Color1",
                                                                    "Reroute",
                                                                    "Output"
                                                                ],
                                                                [
                                                                    "Color2",
                                                                    "Reroute.001",
                                                                    "Output"
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "NodeGroupOutput",
                                                            "name": "Group Output",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "location": [
                                                                    1233.096435546875,
                                                                    227.01815795898438
                                                                ],
                                                                "select": false
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "Color",
                                                                    "Switch",
                                                                    "Output_004"
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "GeometryNodeSwitch",
                                                            "name": "Switch",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "input_type": "RGBA",
                                                                "location": [
                                                                    500.0,
                                                                    220.0
                                                                ],
                                                                "select": false
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "Switch",
                                                                    "Compare",
                                                                    "Result"
                                                                ],
                                                                [
                                                                    "Switch_001",
                                                                    false
                                                                ],
                                                                [
                                                                    "False",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "True",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "False_001",
                                                                    0
                                                                ],
                                                                [
                                                                    "True_001",
                                                                    0
                                                                ],
                                                                [
                                                                    "False_002",
                                                                    false
                                                                ],
                                                                [
                                                                    "True_002",
                                                                    true
                                                                ],
                                                                [
                                                                    "False_003",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "True_003",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "False_004",
                                                                    "Switch.001",
                                                                    "Output_004"
                                                                ],
                                                                [
                                                                    "True_004",
                                                                    "mixer",
                                                                    "Color"
                                                                ],
                                                                [
                                                                    "False_005",
                                                                    ""
                                                                ],
                                                                [
                                                                    "True_005",
                                                                    ""
                                                                ],
                                                                [
                                                                    "False_006",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_006",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_007",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_007",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_008",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_008",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_009",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_009",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_010",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_010",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_011",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_011",
                                                                    null
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "NodeReroute",
                                                            "name": "Reroute.001",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "location": [
                                                                    -1658.7674560546875,
                                                                    23.490371704101562
                                                                ],
                                                                "select": false,
                                                                "width": 100.0
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "Input",
                                                                    "invert",
                                                                    "Output_004"
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "NodeReroute",
                                                            "name": "Reroute",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "location": [
                                                                    -1636.0419921875,
                                                                    43.88283920288086
                                                                ],
                                                                "select": false,
                                                                "width": 100.0
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "Input",
                                                                    "Group Input",
                                                                    "Color1"
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "GeometryNodeSwitch",
                                                            "name": "invert",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "input_type": "RGBA",
                                                                "location": [
                                                                    -1875.9127197265625,
                                                                    -7.148228645324707
                                                                ],
                                                                "select": false
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "Switch",
                                                                    "Group Input",
                                                                    "_invert"
                                                                ],
                                                                [
                                                                    "Switch_001",
                                                                    false
                                                                ],
                                                                [
                                                                    "False",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "True",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "False_001",
                                                                    0
                                                                ],
                                                                [
                                                                    "True_001",
                                                                    0
                                                                ],
                                                                [
                                                                    "False_002",
                                                                    false
                                                                ],
                                                                [
                                                                    "True_002",
                                                                    true
                                                                ],
                                                                [
                                                                    "False_003",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "True_003",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "False_004",
                                                                    "Group Input",
                                                                    "Color2"
                                                                ],
                                                                [
                                                                    "True_004",
                                                                    "ColorRamp",
                                                                    "Color"
                                                                ],
                                                                [
                                                                    "False_005",
                                                                    ""
                                                                ],
                                                                [
                                                                    "True_005",
                                                                    ""
                                                                ],
                                                                [
                                                                    "False_006",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_006",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_007",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_007",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_008",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_008",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_009",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_009",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_010",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_010",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_011",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_011",
                                                                    null
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "ShaderNodeValToRGB",
                                                            "name": "ColorRamp",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "location": [
                                                                    -2233.688720703125,
                                                                    -98.2742919921875
                                                                ],
                                                                "select": false
                                                            },
                                                            "color_ramp": [
                                                                [
                                                                    0.0,
                                                                    [
                                                                        1.0,
                                                                        1.0,
                                                                        1.0,
                                                                        1.0
                                                                    ]
                                                                ],
                                                                [
                                                                    1.0,
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0,
                                                                        1.0
                                                                    ]
                                                                ]
                                                            ],
                                                            "inputs": [
                                                                [
                                                                    "Fac",
                                                                    "Group Input",
                                                                    "Color2"
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "NodeGroupInput",
                                                            "name": "Group Input",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "location": [
                                                                    -2450.174072265625,
                                                                    238.57168579101562
                                                                ],
                                                                "select": false
                                                            }
                                                        }
                                                    ],
                                                    "inputs": [
                                                        {
                                                            "name": "_influence",
                                                            "type": "NodeSocketFloatFactor",
                                                            "identifier": "Input_0",
                                                            "default": 1.0,
                                                            "min": 0.0,
                                                            "max": 1.0
                                                        },
                                                        {
                                                            "name": "_blend_type",
                                                            "type": "NodeSocketString",
                                                            "identifier": "Input_1",
                                                            "default": "MIX"
                                                        },
                                                        {
                                                            "name": "_invert",
                                                            "type": "NodeSocketBool",
                                                            "identifier": "Input_2",
                                                            "default": false
                                                        },
                                                        {
                                                            "name": "Color1",
                                                            "type": "NodeSocketColor",
                                                            "identifier": "Input_3",
                                                            "default": [
                                                                0.5,
                                                                0.5,
                                                                0.5,
                                                                1.0
                                                            ]
                                                        },
                                                        {
                                                            "name": "Color2",
                                                            "type": "NodeSocketColor",
                                                            "identifier": "Input_4",
                                                            "default": [
                                                                0.5,
                                                                0.5,
                                                                0.5,
                                                                1.0
                                                            ]
                                                        }
                                                    ],
                                                    "outputs": [
                                                        {
                                                            "name": "Color",
                                                            "type": "NodeSocketColor",
                                                            "identifier": "Output_5"
                                                        }
                                                    ]
                                                },
                                                "props": {
                                                    "display_in_effect": false,
                                                    "display_order": 0,
                                                    "location": [
                                                        -80.0,
                                                        -320.0
                                                    ]
                                                },
                                                "inputs": [
                                                    [
                                                        "Input_0",
                                                        1.0
                                                    ],
                                                    [
                                                        "Input_1",
                                                        "MIX"
                                                    ],
                                                    [
                                                        "Input_2",
                                                        false
                                                    ],
                                                    [
                                                        "Color1",
                                                        "Node.001",
                                                        "Attribute_Float"
                                                    ],
                                                    [
                                                        "Color2",
                                                        "Reroute",
                                                        "Output"
                                                    ]
                                                ]
                                            },
                                            {
                                                "type": "GeometryNodeSwitch",
                                                "name": "Switch",
                                                "label": "",
                                                "props": {
                                                    "display_in_effect": false,
                                                    "display_order": 0,
                                                    "location": [
                                                        635.2285766601562,
                                                        128.86436462402344
                                                    ],
                                                    "select": false
                                                },
                                                "inputs": [
                                                    [
                                                        "Switch",
                                                        false
                                                    ],
                                                    [
                                                        "Switch_001",
                                                        false
                                                    ],
                                                    [
                                                        "False",
                                                        0.0
                                                    ],
                                                    [
                                                        "True",
                                                        0.0
                                                    ],
                                                    [
                                                        "False_001",
                                                        0
                                                    ],
                                                    [
                                                        "True_001",
                                                        0
                                                    ],
                                                    [
                                                        "False_002",
                                                        false
                                                    ],
                                                    [
                                                        "True_002",
                                                        true
                                                    ],
                                                    [
                                                        "False_003",
                                                        [
                                                            0.0,
                                                            0.0,
                                                            0.0
                                                        ]
                                                    ],
                                                    [
                                                        "True_003",
                                                        [
                                                            0.0,
                                                            0.0,
                                                            0.0
                                                        ]
                                                    ],
                                                    [
                                                        "False_004",
                                                        [
                                                            0.800000011920929,
                                                            0.800000011920929,
                                                            0.800000011920929,
                                                            1.0
                                                        ]
                                                    ],
                                                    [
                                                        "True_004",
                                                        [
                                                            0.800000011920929,
                                                            0.800000011920929,
                                                            0.800000011920929,
                                                            1.0
                                                        ]
                                                    ],
                                                    [
                                                        "False_005",
                                                        ""
                                                    ],
                                                    [
                                                        "True_005",
                                                        ""
                                                    ],
                                                    [
                                                        "False_006",
                                                        "Group Input",
                                                        "Original Geometry"
                                                    ],
                                                    [
                                                        "True_006",
                                                        "Node",
                                                        "Geometry"
                                                    ],
                                                    [
                                                        "False_007",
                                                        null
                                                    ],
                                                    [
                                                        "True_007",
                                                        null
                                                    ],
                                                    [
                                                        "False_008",
                                                        null
                                                    ],
                                                    [
                                                        "True_008",
                                                        null
                                                    ],
                                                    [
                                                        "False_009",
                                                        null
                                                    ],
                                                    [
                                                        "True_009",
                                                        null
                                                    ],
                                                    [
                                                        "False_010",
                                                        null
                                                    ],
                                                    [
                                                        "True_010",
                                                        null
                                                    ],
                                                    [
                                                        "False_011",
                                                        null
                                                    ],
                                                    [
                                                        "True_011",
                                                        null
                                                    ]
                                                ]
                                            },
                                            {
                                                "type": "GeometryNodeGroup",
                                                "name": "visualization_mixer",
                                                "label": "",
                                                "node_group": {
                                                    "name": "mixer.023",
                                                    "nodes": [
                                                        {
                                                            "type": "ShaderNodeMixRGB",
                                                            "name": "mixer.002",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "blend_type": "MULTIPLY",
                                                                "location": [
                                                                    20.0,
                                                                    40.0
                                                                ],
                                                                "select": false
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "Fac",
                                                                    "Group Input",
                                                                    "_influence"
                                                                ],
                                                                [
                                                                    "Color1",
                                                                    "Reroute",
                                                                    "Output"
                                                                ],
                                                                [
                                                                    "Color2",
                                                                    "Reroute.001",
                                                                    "Output"
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "GeometryNodeSwitch",
                                                            "name": "Switch.002",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "input_type": "RGBA",
                                                                "location": [
                                                                    20.0,
                                                                    220.0
                                                                ],
                                                                "select": false
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "Switch",
                                                                    "Compare.002",
                                                                    "Result"
                                                                ],
                                                                [
                                                                    "Switch_001",
                                                                    false
                                                                ],
                                                                [
                                                                    "False",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "True",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "False_001",
                                                                    0
                                                                ],
                                                                [
                                                                    "True_001",
                                                                    0
                                                                ],
                                                                [
                                                                    "False_002",
                                                                    false
                                                                ],
                                                                [
                                                                    "True_002",
                                                                    true
                                                                ],
                                                                [
                                                                    "False_003",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "True_003",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "False_004",
                                                                    "Switch.003",
                                                                    "Output_004"
                                                                ],
                                                                [
                                                                    "True_004",
                                                                    "mixer.002",
                                                                    "Color"
                                                                ],
                                                                [
                                                                    "False_005",
                                                                    ""
                                                                ],
                                                                [
                                                                    "True_005",
                                                                    ""
                                                                ],
                                                                [
                                                                    "False_006",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_006",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_007",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_007",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_008",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_008",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_009",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_009",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_010",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_010",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_011",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_011",
                                                                    null
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "FunctionNodeCompare",
                                                            "name": "Compare.002",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "data_type": "STRING",
                                                                "location": [
                                                                    20.0,
                                                                    400.0
                                                                ],
                                                                "operation": "EQUAL",
                                                                "select": false
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "A",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "B",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "A_INT",
                                                                    0
                                                                ],
                                                                [
                                                                    "B_INT",
                                                                    0
                                                                ],
                                                                [
                                                                    "A_VEC3",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "B_VEC3",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "A_COL",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "B_COL",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "A_STR",
                                                                    "Group Input",
                                                                    "_blend_type"
                                                                ],
                                                                [
                                                                    "B_STR",
                                                                    "MULTIPLY"
                                                                ],
                                                                [
                                                                    "C",
                                                                    0.8999999761581421
                                                                ],
                                                                [
                                                                    "Angle",
                                                                    0.08726649731397629
                                                                ],
                                                                [
                                                                    "Epsilon",
                                                                    0.0010000000474974513
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "GeometryNodeSwitch",
                                                            "name": "Switch.003",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "input_type": "RGBA",
                                                                "location": [
                                                                    -220.0,
                                                                    220.0
                                                                ],
                                                                "select": false
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "Switch",
                                                                    "Compare.003",
                                                                    "Result"
                                                                ],
                                                                [
                                                                    "Switch_001",
                                                                    false
                                                                ],
                                                                [
                                                                    "False",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "True",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "False_001",
                                                                    0
                                                                ],
                                                                [
                                                                    "True_001",
                                                                    0
                                                                ],
                                                                [
                                                                    "False_002",
                                                                    false
                                                                ],
                                                                [
                                                                    "True_002",
                                                                    true
                                                                ],
                                                                [
                                                                    "False_003",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "True_003",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "False_004",
                                                                    "Switch.004",
                                                                    "Output_004"
                                                                ],
                                                                [
                                                                    "True_004",
                                                                    "mixer.003",
                                                                    "Color"
                                                                ],
                                                                [
                                                                    "False_005",
                                                                    ""
                                                                ],
                                                                [
                                                                    "True_005",
                                                                    ""
                                                                ],
                                                                [
                                                                    "False_006",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_006",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_007",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_007",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_008",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_008",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_009",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_009",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_010",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_010",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_011",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_011",
                                                                    null
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "ShaderNodeMixRGB",
                                                            "name": "mixer.003",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "blend_type": "ADD",
                                                                "location": [
                                                                    -220.0,
                                                                    40.0
                                                                ],
                                                                "select": false
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "Fac",
                                                                    "Group Input",
                                                                    "_influence"
                                                                ],
                                                                [
                                                                    "Color1",
                                                                    "Reroute",
                                                                    "Output"
                                                                ],
                                                                [
                                                                    "Color2",
                                                                    "Reroute.001",
                                                                    "Output"
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "FunctionNodeCompare",
                                                            "name": "Compare.003",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "data_type": "STRING",
                                                                "location": [
                                                                    -220.0,
                                                                    400.0
                                                                ],
                                                                "operation": "EQUAL",
                                                                "select": false
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "A",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "B",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "A_INT",
                                                                    0
                                                                ],
                                                                [
                                                                    "B_INT",
                                                                    0
                                                                ],
                                                                [
                                                                    "A_VEC3",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "B_VEC3",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "A_COL",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "B_COL",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "A_STR",
                                                                    "Group Input",
                                                                    "_blend_type"
                                                                ],
                                                                [
                                                                    "B_STR",
                                                                    "ADD"
                                                                ],
                                                                [
                                                                    "C",
                                                                    0.8999999761581421
                                                                ],
                                                                [
                                                                    "Angle",
                                                                    0.08726649731397629
                                                                ],
                                                                [
                                                                    "Epsilon",
                                                                    0.0010000000474974513
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "GeometryNodeSwitch",
                                                            "name": "Switch.004",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "input_type": "RGBA",
                                                                "location": [
                                                                    -460.0,
                                                                    220.0
                                                                ],
                                                                "select": false
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "Switch",
                                                                    "Compare.004",
                                                                    "Result"
                                                                ],
                                                                [
                                                                    "Switch_001",
                                                                    false
                                                                ],
                                                                [
                                                                    "False",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "True",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "False_001",
                                                                    0
                                                                ],
                                                                [
                                                                    "True_001",
                                                                    0
                                                                ],
                                                                [
                                                                    "False_002",
                                                                    false
                                                                ],
                                                                [
                                                                    "True_002",
                                                                    true
                                                                ],
                                                                [
                                                                    "False_003",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "True_003",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "False_004",
                                                                    "Switch.005",
                                                                    "Output_004"
                                                                ],
                                                                [
                                                                    "True_004",
                                                                    "mixer.004",
                                                                    "Color"
                                                                ],
                                                                [
                                                                    "False_005",
                                                                    ""
                                                                ],
                                                                [
                                                                    "True_005",
                                                                    ""
                                                                ],
                                                                [
                                                                    "False_006",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_006",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_007",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_007",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_008",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_008",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_009",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_009",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_010",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_010",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_011",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_011",
                                                                    null
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "ShaderNodeMixRGB",
                                                            "name": "mixer.004",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "blend_type": "DIVIDE",
                                                                "location": [
                                                                    -460.0,
                                                                    40.0
                                                                ],
                                                                "select": false
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "Fac",
                                                                    "Group Input",
                                                                    "_influence"
                                                                ],
                                                                [
                                                                    "Color1",
                                                                    "Reroute",
                                                                    "Output"
                                                                ],
                                                                [
                                                                    "Color2",
                                                                    "Reroute.001",
                                                                    "Output"
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "FunctionNodeCompare",
                                                            "name": "Compare.004",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "data_type": "STRING",
                                                                "location": [
                                                                    -460.0,
                                                                    400.0
                                                                ],
                                                                "operation": "EQUAL",
                                                                "select": false
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "A",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "B",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "A_INT",
                                                                    0
                                                                ],
                                                                [
                                                                    "B_INT",
                                                                    0
                                                                ],
                                                                [
                                                                    "A_VEC3",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "B_VEC3",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "A_COL",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "B_COL",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "A_STR",
                                                                    "Group Input",
                                                                    "_blend_type"
                                                                ],
                                                                [
                                                                    "B_STR",
                                                                    "DIVIDE"
                                                                ],
                                                                [
                                                                    "C",
                                                                    0.8999999761581421
                                                                ],
                                                                [
                                                                    "Angle",
                                                                    0.08726649731397629
                                                                ],
                                                                [
                                                                    "Epsilon",
                                                                    0.0010000000474974513
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "ShaderNodeMixRGB",
                                                            "name": "mixer.001",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "blend_type": "DARKEN",
                                                                "location": [
                                                                    260.0,
                                                                    40.0
                                                                ],
                                                                "select": false
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "Fac",
                                                                    "Group Input",
                                                                    "_influence"
                                                                ],
                                                                [
                                                                    "Color1",
                                                                    "Reroute.001",
                                                                    "Output"
                                                                ],
                                                                [
                                                                    "Color2",
                                                                    "Reroute",
                                                                    "Output"
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "GeometryNodeSwitch",
                                                            "name": "Switch.001",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "input_type": "RGBA",
                                                                "location": [
                                                                    260.0,
                                                                    220.0
                                                                ],
                                                                "select": false
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "Switch",
                                                                    "Compare.001",
                                                                    "Result"
                                                                ],
                                                                [
                                                                    "Switch_001",
                                                                    false
                                                                ],
                                                                [
                                                                    "False",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "True",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "False_001",
                                                                    0
                                                                ],
                                                                [
                                                                    "True_001",
                                                                    0
                                                                ],
                                                                [
                                                                    "False_002",
                                                                    false
                                                                ],
                                                                [
                                                                    "True_002",
                                                                    true
                                                                ],
                                                                [
                                                                    "False_003",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "True_003",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "False_004",
                                                                    "Switch.002",
                                                                    "Output_004"
                                                                ],
                                                                [
                                                                    "True_004",
                                                                    "mixer.001",
                                                                    "Color"
                                                                ],
                                                                [
                                                                    "False_005",
                                                                    ""
                                                                ],
                                                                [
                                                                    "True_005",
                                                                    ""
                                                                ],
                                                                [
                                                                    "False_006",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_006",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_007",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_007",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_008",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_008",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_009",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_009",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_010",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_010",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_011",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_011",
                                                                    null
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "FunctionNodeCompare",
                                                            "name": "Compare",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "data_type": "STRING",
                                                                "location": [
                                                                    500.0,
                                                                    400.0
                                                                ],
                                                                "operation": "EQUAL",
                                                                "select": false
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "A",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "B",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "A_INT",
                                                                    0
                                                                ],
                                                                [
                                                                    "B_INT",
                                                                    0
                                                                ],
                                                                [
                                                                    "A_VEC3",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "B_VEC3",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "A_COL",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "B_COL",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "A_STR",
                                                                    "Group Input",
                                                                    "_blend_type"
                                                                ],
                                                                [
                                                                    "B_STR",
                                                                    "MIX"
                                                                ],
                                                                [
                                                                    "C",
                                                                    0.8999999761581421
                                                                ],
                                                                [
                                                                    "Angle",
                                                                    0.08726649731397629
                                                                ],
                                                                [
                                                                    "Epsilon",
                                                                    0.0010000000474974513
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "ShaderNodeMixRGB",
                                                            "name": "mixer",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "location": [
                                                                    500.0,
                                                                    40.0
                                                                ],
                                                                "select": false
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "Fac",
                                                                    "Group Input",
                                                                    "_influence"
                                                                ],
                                                                [
                                                                    "Color1",
                                                                    "Reroute",
                                                                    "Output"
                                                                ],
                                                                [
                                                                    "Color2",
                                                                    "Reroute.001",
                                                                    "Output"
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "FunctionNodeCompare",
                                                            "name": "Compare.001",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "data_type": "STRING",
                                                                "location": [
                                                                    260.0,
                                                                    400.0
                                                                ],
                                                                "operation": "EQUAL",
                                                                "select": false
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "A",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "B",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "A_INT",
                                                                    0
                                                                ],
                                                                [
                                                                    "B_INT",
                                                                    0
                                                                ],
                                                                [
                                                                    "A_VEC3",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "B_VEC3",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "A_COL",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "B_COL",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "A_STR",
                                                                    "Group Input",
                                                                    "_blend_type"
                                                                ],
                                                                [
                                                                    "B_STR",
                                                                    "DARKEN"
                                                                ],
                                                                [
                                                                    "C",
                                                                    0.8999999761581421
                                                                ],
                                                                [
                                                                    "Angle",
                                                                    0.08726649731397629
                                                                ],
                                                                [
                                                                    "Epsilon",
                                                                    0.0010000000474974513
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "ShaderNodeMixRGB",
                                                            "name": "mixer.005",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "blend_type": "SUBTRACT",
                                                                "location": [
                                                                    -700.0,
                                                                    40.0
                                                                ],
                                                                "select": false
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "Fac",
                                                                    "Group Input",
                                                                    "_influence"
                                                                ],
                                                                [
                                                                    "Color1",
                                                                    "Reroute",
                                                                    "Output"
                                                                ],
                                                                [
                                                                    "Color2",
                                                                    "Reroute.001",
                                                                    "Output"
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "FunctionNodeCompare",
                                                            "name": "Compare.005",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "data_type": "STRING",
                                                                "location": [
                                                                    -700.0,
                                                                    400.0
                                                                ],
                                                                "operation": "EQUAL",
                                                                "select": false
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "A",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "B",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "A_INT",
                                                                    0
                                                                ],
                                                                [
                                                                    "B_INT",
                                                                    0
                                                                ],
                                                                [
                                                                    "A_VEC3",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "B_VEC3",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "A_COL",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "B_COL",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "A_STR",
                                                                    "Group Input",
                                                                    "_blend_type"
                                                                ],
                                                                [
                                                                    "B_STR",
                                                                    "SUBTRACT"
                                                                ],
                                                                [
                                                                    "C",
                                                                    0.8999999761581421
                                                                ],
                                                                [
                                                                    "Angle",
                                                                    0.08726649731397629
                                                                ],
                                                                [
                                                                    "Epsilon",
                                                                    0.0010000000474974513
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "GeometryNodeSwitch",
                                                            "name": "Switch.005",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "input_type": "RGBA",
                                                                "location": [
                                                                    -700.0,
                                                                    220.0
                                                                ],
                                                                "select": false
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "Switch",
                                                                    "Compare.005",
                                                                    "Result"
                                                                ],
                                                                [
                                                                    "Switch_001",
                                                                    false
                                                                ],
                                                                [
                                                                    "False",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "True",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "False_001",
                                                                    0
                                                                ],
                                                                [
                                                                    "True_001",
                                                                    0
                                                                ],
                                                                [
                                                                    "False_002",
                                                                    false
                                                                ],
                                                                [
                                                                    "True_002",
                                                                    true
                                                                ],
                                                                [
                                                                    "False_003",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "True_003",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "False_004",
                                                                    "Switch.006",
                                                                    "Output_004"
                                                                ],
                                                                [
                                                                    "True_004",
                                                                    "mixer.005",
                                                                    "Color"
                                                                ],
                                                                [
                                                                    "False_005",
                                                                    ""
                                                                ],
                                                                [
                                                                    "True_005",
                                                                    ""
                                                                ],
                                                                [
                                                                    "False_006",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_006",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_007",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_007",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_008",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_008",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_009",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_009",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_010",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_010",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_011",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_011",
                                                                    null
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "FunctionNodeCompare",
                                                            "name": "Compare.006",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "data_type": "STRING",
                                                                "location": [
                                                                    -960.0,
                                                                    400.0
                                                                ],
                                                                "operation": "EQUAL",
                                                                "select": false
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "A",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "B",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "A_INT",
                                                                    0
                                                                ],
                                                                [
                                                                    "B_INT",
                                                                    0
                                                                ],
                                                                [
                                                                    "A_VEC3",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "B_VEC3",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "A_COL",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "B_COL",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "A_STR",
                                                                    "Group Input",
                                                                    "_blend_type"
                                                                ],
                                                                [
                                                                    "B_STR",
                                                                    "DIFFERENCE"
                                                                ],
                                                                [
                                                                    "C",
                                                                    0.8999999761581421
                                                                ],
                                                                [
                                                                    "Angle",
                                                                    0.08726649731397629
                                                                ],
                                                                [
                                                                    "Epsilon",
                                                                    0.0010000000474974513
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "GeometryNodeSwitch",
                                                            "name": "Switch.006",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "input_type": "RGBA",
                                                                "location": [
                                                                    -960.0,
                                                                    220.0
                                                                ],
                                                                "select": false
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "Switch",
                                                                    "Compare.006",
                                                                    "Result"
                                                                ],
                                                                [
                                                                    "Switch_001",
                                                                    false
                                                                ],
                                                                [
                                                                    "False",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "True",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "False_001",
                                                                    0
                                                                ],
                                                                [
                                                                    "True_001",
                                                                    0
                                                                ],
                                                                [
                                                                    "False_002",
                                                                    false
                                                                ],
                                                                [
                                                                    "True_002",
                                                                    true
                                                                ],
                                                                [
                                                                    "False_003",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "True_003",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "False_004",
                                                                    "mixer.007",
                                                                    "Color"
                                                                ],
                                                                [
                                                                    "True_004",
                                                                    "mixer.006",
                                                                    "Color"
                                                                ],
                                                                [
                                                                    "False_005",
                                                                    ""
                                                                ],
                                                                [
                                                                    "True_005",
                                                                    ""
                                                                ],
                                                                [
                                                                    "False_006",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_006",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_007",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_007",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_008",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_008",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_009",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_009",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_010",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_010",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_011",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_011",
                                                                    null
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "ShaderNodeMixRGB",
                                                            "name": "mixer.006",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "blend_type": "DIFFERENCE",
                                                                "location": [
                                                                    -960.0,
                                                                    40.0
                                                                ],
                                                                "select": false
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "Fac",
                                                                    "Group Input",
                                                                    "_influence"
                                                                ],
                                                                [
                                                                    "Color1",
                                                                    "Reroute",
                                                                    "Output"
                                                                ],
                                                                [
                                                                    "Color2",
                                                                    "Reroute.001",
                                                                    "Output"
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "ShaderNodeMixRGB",
                                                            "name": "mixer.007",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "location": [
                                                                    -1200.0,
                                                                    160.0
                                                                ],
                                                                "select": false
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "Fac",
                                                                    "Group Input",
                                                                    "_influence"
                                                                ],
                                                                [
                                                                    "Color1",
                                                                    "Reroute",
                                                                    "Output"
                                                                ],
                                                                [
                                                                    "Color2",
                                                                    "Reroute.001",
                                                                    "Output"
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "NodeGroupOutput",
                                                            "name": "Group Output",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "location": [
                                                                    1233.096435546875,
                                                                    227.01815795898438
                                                                ],
                                                                "select": false
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "Color",
                                                                    "Switch",
                                                                    "Output_004"
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "GeometryNodeSwitch",
                                                            "name": "Switch",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "input_type": "RGBA",
                                                                "location": [
                                                                    500.0,
                                                                    220.0
                                                                ],
                                                                "select": false
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "Switch",
                                                                    "Compare",
                                                                    "Result"
                                                                ],
                                                                [
                                                                    "Switch_001",
                                                                    false
                                                                ],
                                                                [
                                                                    "False",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "True",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "False_001",
                                                                    0
                                                                ],
                                                                [
                                                                    "True_001",
                                                                    0
                                                                ],
                                                                [
                                                                    "False_002",
                                                                    false
                                                                ],
                                                                [
                                                                    "True_002",
                                                                    true
                                                                ],
                                                                [
                                                                    "False_003",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "True_003",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "False_004",
                                                                    "Switch.001",
                                                                    "Output_004"
                                                                ],
                                                                [
                                                                    "True_004",
                                                                    "mixer",
                                                                    "Color"
                                                                ],
                                                                [
                                                                    "False_005",
                                                                    ""
                                                                ],
                                                                [
                                                                    "True_005",
                                                                    ""
                                                                ],
                                                                [
                                                                    "False_006",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_006",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_007",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_007",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_008",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_008",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_009",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_009",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_010",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_010",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_011",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_011",
                                                                    null
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "NodeReroute",
                                                            "name": "Reroute.001",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "location": [
                                                                    -1658.7674560546875,
                                                                    23.490371704101562
                                                                ],
                                                                "select": false,
                                                                "width": 100.0
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "Input",
                                                                    "invert",
                                                                    "Output_004"
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "NodeReroute",
                                                            "name": "Reroute",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "location": [
                                                                    -1636.0419921875,
                                                                    43.88283920288086
                                                                ],
                                                                "select": false,
                                                                "width": 100.0
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "Input",
                                                                    "Group Input",
                                                                    "Color1"
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "GeometryNodeSwitch",
                                                            "name": "invert",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "input_type": "RGBA",
                                                                "location": [
                                                                    -1875.9127197265625,
                                                                    -7.148228645324707
                                                                ],
                                                                "select": false
                                                            },
                                                            "inputs": [
                                                                [
                                                                    "Switch",
                                                                    "Group Input",
                                                                    "_invert"
                                                                ],
                                                                [
                                                                    "Switch_001",
                                                                    false
                                                                ],
                                                                [
                                                                    "False",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "True",
                                                                    0.0
                                                                ],
                                                                [
                                                                    "False_001",
                                                                    0
                                                                ],
                                                                [
                                                                    "True_001",
                                                                    0
                                                                ],
                                                                [
                                                                    "False_002",
                                                                    false
                                                                ],
                                                                [
                                                                    "True_002",
                                                                    true
                                                                ],
                                                                [
                                                                    "False_003",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "True_003",
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0
                                                                    ]
                                                                ],
                                                                [
                                                                    "False_004",
                                                                    "Group Input",
                                                                    "Color2"
                                                                ],
                                                                [
                                                                    "True_004",
                                                                    "ColorRamp",
                                                                    "Color"
                                                                ],
                                                                [
                                                                    "False_005",
                                                                    ""
                                                                ],
                                                                [
                                                                    "True_005",
                                                                    ""
                                                                ],
                                                                [
                                                                    "False_006",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_006",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_007",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_007",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_008",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_008",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_009",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_009",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_010",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_010",
                                                                    null
                                                                ],
                                                                [
                                                                    "False_011",
                                                                    null
                                                                ],
                                                                [
                                                                    "True_011",
                                                                    null
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "ShaderNodeValToRGB",
                                                            "name": "ColorRamp",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "location": [
                                                                    -2233.688720703125,
                                                                    -98.2742919921875
                                                                ],
                                                                "select": false
                                                            },
                                                            "color_ramp": [
                                                                [
                                                                    0.0,
                                                                    [
                                                                        1.0,
                                                                        1.0,
                                                                        1.0,
                                                                        1.0
                                                                    ]
                                                                ],
                                                                [
                                                                    1.0,
                                                                    [
                                                                        0.0,
                                                                        0.0,
                                                                        0.0,
                                                                        1.0
                                                                    ]
                                                                ]
                                                            ],
                                                            "inputs": [
                                                                [
                                                                    "Fac",
                                                                    "Group Input",
                                                                    "Color2"
                                                                ]
                                                            ]
                                                        },
                                                        {
                                                            "type": "NodeGroupInput",
                                                            "name": "Group Input",
                                                            "label": "",
                                                            "props": {
                                                                "display_in_effect": false,
                                                                "display_order": 0,
                                                                "location": [
                                                                    -2450.174072265625,
                                                                    238.57168579101562
                                                                ],
                                                                "select": false
                                                            }
                                                        }
                                                    ],
                                                    "inputs": [
                                                        {
                                                            "name": "_influence",
                                                            "type": "NodeSocketFloatFactor",
                                                            "identifier": "Input_0",
                                                            "default": 1.0,
                                                            "min": 0.0,
                                                            "max": 1.0
                                                        },
                                                        {
                                                            "name": "_blend_type",
                                                            "type": "NodeSocketString",
                                                            "identifier": "Input_1",
                                                            "default": "MIX"
                                                        },
                                                        {
                                                            "name": "_invert",
                                                            "type": "NodeSocketBool",
                                                            "identifier": "Input_2",
                                                            "default": false
                                                        },
                                                        {
                                                            "name": "Color1",
                                                            "type": "NodeSocketColor",
                                                            "identifier": "Input_3",
                                                            "default": [
                                                                0.5,
                                                                0.5,
                                                                0.5,
                                                                1.0
                                                            ]
                                                        },
                                                        {
                                                            "name": "Color2",
                                                            "type": "NodeSocketColor",
                                                            "identifier": "Input_4",
                                                            "default": [
                                                                0.5,
                                                                0.5,
                                                                0.5,
                                                                1.0
                                                            ]
                                                        }
                                                    ],
                                                    "outputs": [
                                                        {
                                                            "name": "Color",
                                                            "type": "NodeSocketColor",
                                                            "identifier": "Output_5"
                                                        }
                                                    ]
                                                },
                                                "props": {
                                                    "display_in_effect": false,
                                                    "display_order": 0,
                                                    "location": [
                                                        0.0,
                                                        260.0
                                                    ]
                                                },
                                                "inputs": [
                                                    [
                                                        "Input_0",
                                                        1.0
                                                    ],
                                                    [
                                                        "Input_1",
                                                        "MIX"
                                                    ],
                                                    [
                                                        "Input_2",
                                                        false
                                                    ],
                                                    [
                                                        "Color1",
                                                        "Named Attribute.001",
                                                        "Attribute_Float"
                                                    ],
                                                    [
                                                        "Color2",
                                                        "Group Input",
                                                        "Data"
                                                    ]
                                                ]
                                            },
                                            {
                                                "type": "NodeGroupOutput",
                                                "name": "Group Output",
                                                "label": "",
                                                "props": {
                                                    "display_in_effect": false,
                                                    "display_order": 0,
                                                    "location": [
                                                        915.4483642578125,
                                                        -78.79230499267578
                                                    ],
                                                    "select": false
                                                },
                                                "inputs": [
                                                    [
                                                        "Main Geometry",
                                                        "Store Named Attribute.001",
                                                        "Geometry"
                                                    ],
                                                    [
                                                        "Original Geometry",
                                                        "Switch",
                                                        "Output_006"
                                                    ]
                                                ]
                                            },
                                            {
                                                "type": "GeometryNodeStoreNamedAttribute",
                                                "name": "Store Named Attribute.001",
                                                "label": "",
                                                "props": {
                                                    "display_in_effect": false,
                                                    "display_order": 0,
                                                    "location": [
                                                        280.0,
                                                        -100.0
                                                    ],
                                                    "select": false
                                                },
                                                "inputs": [
                                                    [
                                                        "Geometry",
                                                        "Group Input",
                                                        "Main Geometry"
                                                    ],
                                                    [
                                                        "Name",
                                                        "channel",
                                                        "String"
                                                    ],
                                                    [
                                                        "Value_Vector",
                                                        [
                                                            0.0,
                                                            0.0,
                                                            0.0
                                                        ]
                                                    ],
                                                    [
                                                        "Value_Float",
                                                        "mixer",
                                                        "Color"
                                                    ],
                                                    [
                                                        "Value_Color",
                                                        [
                                                            0.0,
                                                            0.0,
                                                            0.0,
                                                            0.0
                                                        ]
                                                    ],
                                                    [
                                                        "Value_Bool",
                                                        false
                                                    ],
                                                    [
                                                        "Value_Int",
                                                        0
                                                    ]
                                                ]
                                            },
                                            {
                                                "type": "GeometryNodeStoreNamedAttribute",
                                                "name": "Node",
                                                "label": "",
                                                "props": {
                                                    "display_in_effect": false,
                                                    "display_order": 0,
                                                    "data_type": "FLOAT_COLOR",
                                                    "location": [
                                                        280.0,
                                                        120.0
                                                    ]
                                                },
                                                "inputs": [
                                                    [
                                                        "Geometry",
                                                        "Group Input",
                                                        "Original Geometry"
                                                    ],
                                                    [
                                                        "Name",
                                                        "Switch.001",
                                                        "Output_005"
                                                    ],
                                                    [
                                                        "Value_Vector",
                                                        [
                                                            0.0,
                                                            0.0,
                                                            0.0
                                                        ]
                                                    ],
                                                    [
                                                        "Value_Float",
                                                        "visualization_mixer",
                                                        "Color"
                                                    ],
                                                    [
                                                        "Value_Color",
                                                        "visualization_mixer",
                                                        "Color"
                                                    ],
                                                    [
                                                        "Value_Bool",
                                                        false
                                                    ],
                                                    [
                                                        "Value_Int",
                                                        0
                                                    ]
                                                ]
                                            }
                                        ],
                                        "inputs": [
                                            {
                                                "name": "Main Geometry",
                                                "type": "NodeSocketGeometry",
                                                "identifier": "Input_0"
                                            },
                                            {
                                                "name": "Original Geometry",
                                                "type": "NodeSocketGeometry",
                                                "identifier": "Input_1"
                                            },
                                            {
                                                "name": "Data",
                                                "type": "NodeSocketFloat",
                                                "identifier": "Input_2",
                                                "default": 0.0
                                            }
                                        ],
                                        "outputs": [
                                            {
                                                "name": "Main Geometry",
                                                "type": "NodeSocketGeometry",
                                                "identifier": "Output_3"
                                            },
                                            {
                                                "name": "Original Geometry",
                                                "type": "NodeSocketGeometry",
                                                "identifier": "Output_4"
                                            }
                                        ]
                                    },
                                    "props": {
                                        "display_in_effect": false,
                                        "display_order": 0,
                                        "location": [
                                            -347.70758056640625,
                                            191.44195556640625
                                        ]
                                    },
                                    "inputs": [
                                        [
                                            "Input_0",
                                            "Group Input",
                                            "Input_0"
                                        ],
                                        [
                                            "Input_1",
                                            "Group Input",
                                            "Input_1"
                                        ],
                                        [
                                            "Input_2",
                                            1.0
                                        ]
                                    ]
                                }
                            ],
                            "inputs": [
                                {
                                    "name": "Main Geometry",
                                    "type": "NodeSocketGeometry",
                                    "identifier": "Input_0"
                                },
                                {
                                    "name": "Original Geometry",
                                    "type": "NodeSocketGeometry",
                                    "identifier": "Input_1"
                                }
                            ],
                            "outputs": [
                                {
                                    "name": "Main Geometry",
                                    "type": "NodeSocketGeometry",
                                    "identifier": "Output_2"
                                },
                                {
                                    "name": "Original Geometry",
                                    "type": "NodeSocketGeometry",
                                    "identifier": "Output_3"
                                }
                            ]
                        }

""")
