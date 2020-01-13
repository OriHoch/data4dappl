$(function () {
    var _allRelatedGroupNames = [];
    $('tr[data-relatedgroupname]').each(function(_, tr) {
        var rgn = $(tr).data('relatedgroupname');
        if (rgn) {
            _allRelatedGroupNames.push(''+rgn);
        }
    });
    _allRelatedGroupNames.push(''+$('#related_entities_table').data('originalgroupname'));
    var onClickRelatedGroup = function ($tr) {
        var $a = $tr.find('a[data-expanded]');
        if ($a.data('expanded')) {
            var deleteGroupNames = [];
            $('#related_entities_table').find('tr').filter(function(_, tr){
                if ($(tr).data('sourcegroupname') && ('' + $(tr).data('sourcegroupname')) === ('' + $tr.data('relatedgroupname'))) {
                    if (deleteGroupNames.indexOf(''+$(tr).data('relatedgroupname')) === -1) {
                        deleteGroupNames.push(''+$(tr).data('relatedgroupname'))
                    }
                    if ($(tr).find('a[data-expanded]').data('expanded')) {
                        onClickRelatedGroup($(tr));
                    }
                    return true;
                }
            }).remove();
            var newRelatedGroupNames = [];
            $.each(_allRelatedGroupNames, function(_, groupName) {
                if (deleteGroupNames.indexOf(''+groupName) === -1) {
                    if (newRelatedGroupNames.indexOf(''+groupName) === -1) {
                        newRelatedGroupNames.push(''+groupName);
                    }
                }
            });
            _allRelatedGroupNames = newRelatedGroupNames;
            $a.data('expanded', false);
            $a.text('('+ $('#related_entities_table').data('expandlabel') +')');
        } else {
            $a.data('expanded', 'true');
            $a.text($('#related_entities_table').data('loadinglabel') + '...');
            $.getJSON('/group/entities/api?name=' + $tr.data('relatedgroupname') + '&reversed=true').then(function (apires) {
                var _table = document.getElementById("related_entities_table");
                var rowIndex = $tr[0].rowIndex+1;
                var numInsertedRows = 0;
                $.each(apires.related_groups, function (_, related_group) {
                    if (_allRelatedGroupNames.indexOf(''+related_group.name) === -1) {
                        _allRelatedGroupNames.push(''+related_group.name);
                        var _row = _table.insertRow(rowIndex);
                        numInsertedRows ++;
                        $(_row).data('sourcegroupname', $tr.data('relatedgroupname'));
                        $(_row).data('relatedgroupname', related_group.name);
                        var _sourceCell = _row.insertCell(0);
                        var _relatedCell = _row.insertCell(1);
                        var _relatedTypeCell = _row.insertCell(2);
                        var _numRelatedEntitiesCell = _row.insertCell(3);
                        var _numRelatedDocumentsCell = _row.insertCell(4);
                        _sourceCell.innerHTML = apires.group.display_name;
                        _relatedCell.innerHTML = '<a href="/group/entities?name=' + related_group.name + '">' + related_group.display_name + '</a>';
                        _relatedTypeCell.innerHTML = '' + related_group.entity_secondary_type;
                        _numRelatedEntitiesCell.innerHTML = '' + related_group.num_related_groups;
                        if (related_group.num_related_groups > 1) {
                            _numRelatedEntitiesCell.innerHTML += ' <a href="javascript:void(0);" data-expanded="false">('+ $(_table).data('expandlabel') +')</a>';
                        }
                        _numRelatedDocumentsCell.innerHTML = '' + related_group.num_datasets;
                        $(_row).find('a[data-expanded]').on('click', function () {
                            onClickRelatedGroup($(_row));
                        });
                    }
                });
                if (numInsertedRows > 0) {
                    $a.text('('+ $('#related_entities_table').data('shrinklabel') +')');
                } else {
                    $a.remove();
                }
            });
        }
    };
    $('#related_entities_table tr[data-relatedgroupname]').each(function (_, tr) {
        $(tr).find('a[data-expanded]').on('click', function () {
            onClickRelatedGroup($(tr));
        });
    });
});

function api_url(param) {
    return "/group/entities/api?name=" + param;
}

function redraw(){
    s.killForceAtlas2();
    s.startForceAtlas2({
        worker: true
    });
    setTimeout(() => { s.stopForceAtlas2() }, 400);
    s.refresh();
}

function highlight_path(src,dest){
    nodes = s.graph.astar(src, dest);
    if (typeof nodes == "undefined") return false;

    // first clear all highlit paths
    _.each(s.graph.edges(), function (e) { e.color = colors.edge });
    _.each(s.graph.nodes(), function (n) { n.color = n.has_groups ? colors.full_node : colors.hollow_node });

    for (var i = 0; i < nodes.length; i++) {
        var n = _.findIndex(s.graph.nodes(), {
            id: nodes[i].id,
        })
        s.graph.nodes()[n].color = colors.lit_node;


        if (i == nodes.length-1) continue;
        var e = _.findIndex(s.graph.edges(), {
            source: nodes[i].id,
            target: nodes[i + 1].id
        })
        s.graph.edges()[e].color = colors.lit_edge;
    }
    s.refresh();

}


function load_nodes_under(node_id) {
    $.getJSON(api_url(node_id), function (odata) {
        var main_node = odata.group;
        var nodes = odata.related_groups;


        if (typeof s.graph.nodes(main_node.name) == "undefined") {
            s.graph.addNode({
                id: main_node.name,
                label: main_node.display_name,
                x: 0,
                y: 0,
                type: 'circle',
                borderColor: colors.border,
                size: 2,
                color: main_node.name == src_node ? colors.lit_node : colors.full_node,
                has_groups: main_node.num_new_related_groups
            })
        }

        nodes.forEach(function (n) {
            if (typeof s.graph.nodes(n.name) == "undefined") {
                s.graph.addNode({
                    id: n.name,
                    label: n.display_name,
                    x: Math.random(),
                    y: Math.random(),
                    type: 'circle',
                    borderColor: colors.border,
                    size: n.num_new_related_groups > 0 ? 2 : 1,
                    color: n.num_new_related_groups > 0 ? colors.full_node : colors.hollow_node,
                    has_groups: n.num_new_related_groups > 0
                });
            }

            s.graph.addEdge({
                    id: main_node.name + '-' + n.name,
                    source: main_node.name,
                    target: n.name,
                    color: colors.edge
            })
        });

        redraw();
        highlight_path(src_node, main_node.name);
    });
}


var colors = {
    border: '#333',
    edge  : '#ccc',
    hollow_node : '#eee',
    full_node   : '#bbb',
    lit_node    : '#c54',
    lit_edge    : '#c54'
}

var s = new sigma({
    renderers: [
        {
            container: document.getElementById('container'),
            type: sigma.renderers.canvas,
        }
    ]
});
var cam = s.cameras[0];

s.settings('drawLabels', true);
s.settings('scalingMode', 'inside');
s.settings('sideMargin', 1);

s.bind("clickNode", function (n) {
    if (n.data.node.has_groups > 0)
        load_nodes_under(n.data.node.id)
});

var listener = s.configNoverlap({
    nodes : s.graph.nodes()
});

var dragListener = new sigma.plugins.dragNodes(s, s.renderers[0]);

// url_params = window.location.search.substring(1).split('&');
// var src_node = url_params[0];
// for now, allow only full screen
// var full_screen = true; //(url_params[1] == 'fullscreen') || false;

// if (!full_screen){
//     document.querySelector('#fullscreen').innerHTML = '<a href="?'+src_node+'&fullscreen" target="_blank">מסך מלא</a>';
// }

src_node = $('#related_entities_table').data('originalgroupname');
load_nodes_under(src_node);
