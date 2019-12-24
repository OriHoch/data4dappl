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

$(function() {
    var svg = d3.select("svg");
    var g 	= svg.append("g");
    var links_class = g.append('g').attr('class', 'links');
    var nodes_class = g.append('g').attr('class', 'nodes');

    var width  = svg.attr("width"),
        height = svg.attr("height");


    var nodes = [];
    var links = [];

    var center_node;

    var simulation = d3.forceSimulation(nodes)
        .force('charge', d3.forceManyBody().strength(-20))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide().radius(30))
        .force('link', d3.forceLink().id(function (d) { return d.id }).links(links))
        .on('tick', render);


    // why isn't this part of remove_node? because we actually want to keep the original node.
    // remove_node is really just a helper
    function remove_children_nodes(node){
        var children = nodes.filter(function(n){ return n.parent == node.id});
        return children.length == 0 ? false : children.forEach(function(n) { remove_children_nodes(n) ; remove_node(n)});
    }

    function remove_node(node){
        links = _.reject(links, function(l) {return (l.source == node || l.target == node) });
        nodes = _.reject(nodes, function(n) {return (n == node || n.parent == node) })
        simulation.nodes(nodes);
        simulation.force('link', d3.forceLink().id(function (d) { return d.id }).links(links))
        simulation.restart();
    }

    function center_on_node(node){
        center_node = node;

        var dcx = (width / 2 - node.x);
        var dcy = (height / 2 - node.y);
        g.transition().attr("transform", "translate(" + dcx + "," + dcy + ")");

        simulation.force('center', d3.forceCenter(center_node.x, center_node.y))
        simulation.alpha(0.1).restart();

        return true;
    }

    function toggle_node(node){
        children = _.where(nodes, {parent:node.id});
        return children.length > 0 ? remove_children_nodes(node) : load_nodes_under(node.id);
    }

    function node_exists(node){
        return (_.findWhere(nodes, {id:node.id}) || false);
    }

    function add_node(new_node, parent=false){
        exists = node_exists(new_node);
        if (exists) return exists;

        i = nodes.push(new_node);
        if (parent) links.push({ source: parent.id, target: new_node.id});

        simulation.nodes(nodes);
        // simulation.force('link', d3.forceLink().id(function (d) { return d.id }).links(links))
        // simulation.alpha(1).restart();

        // console.log("NEW:", nodes[i-1]);
        return nodes[i-1];
    }

    function render() {
        var n = d3.select('.nodes')
            .selectAll('text')
            .data(nodes)

        n.enter()
            .append('text')
            .merge(n)
            .on('click', function (d) { return center_on_node(d) })
            .on('click', function (d) { return toggle_node(d) })
            .text(function (d) { return d.display_name })
            .style('font-size', function (d) { return d.id == center_node.id ? '20px' : '10px' })
            .attr('x', function (d) { return d.x; })
            .attr('y', function (d) { return d.y; });

        n.exit().remove()

        var l = d3.select('.links')
            .selectAll('line')
            .data(links)

        l.enter()
            .append('line')
            .merge(l)
            .attr('x1', function (d) { return d.source.x })
            .attr('y1', function (d) { return d.source.y })
            .attr('x2', function (d) { return d.target.x })
            .attr('y2', function (d) { return d.target.y })

        l.exit().remove()

    }

    function api_url(param){
        return "https://www.odata.org.il/group/entities/api?name=" + param;
    }

    function load_nodes_under(node_id){
        console.log("load_nodes_under:", node_id);
        d3.json(api_url(node_id), function(odata){
            odata.group.id = odata.group.name;
            var new_center = add_node(odata.group, center_node ? center_node : false);
            center_on_node(new_center);

            odata.related_groups.forEach(function (g) {
                g.id = g.name;
                add_node(g, new_center);
            });

        });
    }

    load_nodes_under($('#related_entities_table').data('originalgroupname'));
});