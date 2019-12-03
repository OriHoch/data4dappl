$(function() {
  var onClickRelatedGroup = function($tr) {
    if (!$tr.find('a[data-expanded]').data('expanded')) {
      $tr.find('a[data-expanded]').data('expanded', 'true');
      $tr.find('a[data-expanded]').text('Loading...');
      $.getJSON('/api/3/action/package_search?fq=groups:"'+$tr.data('relatedgroupname')+'"&facet.field=["groups"]&include_private=false&facet.limit=-1&rows=0').then(function(related_query){
          var _table = document.getElementById("related_entities_table");
          $.each(related_query.result.search_facets.groups.items, function(_, related_group) {
              if (
                  related_group.name != $(_table).data('originalgroupname')
                  && related_group.name != $tr.data('relatedgroupname')
                  && $('#related_entities_table tr[data-relatedgroupname='+related_group.name+']').length == 0
              ) {
                var _row = _table.insertRow(-1);
                $(_row).data('relatedgroupname', related_group.name);
                var _sourceCell = _row.insertCell(0);
                var _relatedCell = _row.insertCell(1);
                _sourceCell.innerHTML = $tr.data('relatedgroupdisplayname');
                _relatedCell.innerHTML = '<a href="/group/entities?id='+related_group.name+'">'+related_group.display_name + '</a> (' + related_group.count + ' '+$(_table).data('documentslabel')+') <a href="javascript:void(0)" data-expanded="false">'+$(_table).data('expandlabel')+'</a>';
                $(_row).find('a[data-expanded]').on('click', function() {
                    onClickRelatedGroup($(_row));
                });
              }
          });
          $tr.find('a[data-expanded]').remove();
      });
    }
  };
  $('#related_entities_table tr[data-relatedgroupname]').each(function(_, tr){
    $(tr).find('a[data-expanded]').on('click', function() {
      onClickRelatedGroup($(tr));
    });
  });
});


// function expand_related_groups(source_group_id, source_group_display_name) {
//       $.getJSON('/api/3/action/package_search?fq=groups:"'+source_group_id+'"&facet.field=["groups"]&include_private=false&facet.limit=-1&rows=0').then(function(related_query){
//         $.each(related_query.result.search_facets.groups.items, function(_, related_group) {
//           if (related_group.name != original_group_id && related_group.name != source_group_id) {
//             var _table = document.getElementById("related_entities_table");
//             var _row = _table.insertRow(-1);
//             var _sourceCell = _row.insertCell(0);
//             var _relatedCell = _row.insertCell(1);
//             _sourceCell.innerHTML = source_group_display_name;
//             _relatedCell.innerHTML = related_group.display_name + ' (' + related_group.count + ' {{ _('Documents') }}) <a href="expand_related_groups()"></a>';
//           }
//         });
//       })
//     }