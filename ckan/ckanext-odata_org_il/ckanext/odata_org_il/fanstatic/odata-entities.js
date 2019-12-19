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
            $('#related_entities_table').find('tr').filter(function(_, tr){
                if ($(tr).data('sourcegroupname') && ('' + $(tr).data('sourcegroupname')) === ('' + $tr.data('relatedgroupname'))) {
                    if ($(tr).find('a[data-expanded]').data('expanded')) {
                        onClickRelatedGroup($(tr));
                    }
                    return true;
                }
            }).remove();
            $a.data('expanded', false);
            $a.text('('+ $('#related_entities_table').data('expandlabel') +')');
        } else {
            $a.data('expanded', 'true');
            $a.text($('#related_entities_table').data('loadinglabel') + '...');
            $.getJSON('/group/entities/api?name=' + $tr.data('relatedgroupname') + '&reversed=true').then(function (apires) {
                var _table = document.getElementById("related_entities_table");
                var rowIndex = $tr[0].rowIndex+1;
                $.each(apires.related_groups, function (_, related_group) {
                    // if (_allRelatedGroupNames.indexOf(''+related_group.name) == -1) {
                    //     _allRelatedGroupNames.push(''+related_group.name);
                        var _row = _table.insertRow(rowIndex);
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
                        _numRelatedEntitiesCell.innerHTML = '' + related_group.num_related_groups + ' <a href="javascript:void(0);" data-expanded="false">('+ $(_table).data('expandlabel') +')</a>';
                        _numRelatedDocumentsCell.innerHTML = '' + related_group.num_datasets;
                        $(_row).find('a[data-expanded]').on('click', function () {
                            onClickRelatedGroup($(_row));
                        });
                    // }
                });
                $a.text('('+ $('#related_entities_table').data('shrinklabel') +')');
            });
        }
    };
    $('#related_entities_table tr[data-relatedgroupname]').each(function (_, tr) {
        $(tr).find('a[data-expanded]').on('click', function () {
            onClickRelatedGroup($(tr));
        });
    });
});
