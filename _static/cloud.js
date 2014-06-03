/* ~~~~~~~~~~~~~~
 * cloud.js_t
 * ~~~~~~~~~~~~~~
 *
 * Various bits of javascript driving the moving parts behind various
 * parts of the cloud theme. Handles things such as toggleable sections,
 * collapsing the sidebar, etc.
 *
 * :copyright: Copyright 2011-2012 by Assurance Technologies
 * :license: BSD
 */



  
  


/* ==========================================================================
 * highlighter #2
 * ==========================================================================
 *
 * Sphinx's highlighter marks some objects when user follows link,
 * but doesn't include section names, etc. This catches those.
 */
$(document).ready(function (){
  // helper to locate highlight target based on #fragment
  function locate_target(){
    // find id referenced by #fragment
    var hash = document.location.hash;
    if(!hash) return null;
    var section = document.getElementById(hash.substr(1));
    if(!section) return null;

    // could be div.section, or hidden span at top of div.section
    var name = section.nodeName.toLowerCase();
    if(name != "div"){
      if(name == "span" && section.innerHTML == "" &&
         section.parentNode.nodeName.toLowerCase() == "div"){
        section = section.parentNode;
      }
    }
    // now at section div and either way we have to find title element - h2, h3, etc.
    var children = $(section).children("h2, h3, h4, h5, h6");
    return children.length ? children : null;
  }

  // init highlight
  var target = locate_target();
  if(target) target.addClass("highlighted");

  // update highlight if hash changes
  $(window).bind("hashchange", function () {
    if(target) target.removeClass("highlighted");
    target = locate_target();
    if(target) target.addClass("highlighted");
  });
});

/* ==========================================================================
 * toggleable sections
 * ==========================================================================
 *
 * Added expand/collapse button to any collapsible RST sections.
 * Looks for sections with CSS class "html-toggle",
 * along with the optional classes "expanded" or "collapsed".
 * Button toggles "html-toggle.expanded/collapsed" classes,
 * and relies on CSS to do the rest of the job displaying them as appropriate.
 */

$(document).ready(function (){
  function init(){
    // get header & section, and add static classes
    var header = $(this);
    var section = header.parent();
    header.addClass("html-toggle-button");

    // helper to test if url hash is within this section
    function contains_hash(){
      var hash = document.location.hash;
      return hash && (section[0].id == hash.substr(1) ||
              section.find(hash.replace(/\./g,"\\.")).length>0);
    }

    // helper to control toggle state
    function set_state(expanded){
      if(expanded){
        section.addClass("expanded").removeClass("collapsed");
        section.children().show();
      }else{
        section.addClass("collapsed").removeClass("expanded");
        section.children().hide();
        section.children("span:first-child:empty").show(); /* for :ref: span tag */
        header.show();
      }
    }

    // initialize state
    set_state(section.hasClass("expanded") || contains_hash());

    // bind toggle callback
    header.click(function (){
      set_state(!section.hasClass("expanded"));
      $(window).trigger('cloud-section-toggled', section[0]);
    });

    // open section if user jumps to it from w/in page
    $(window).bind("hashchange", function () {
      if(contains_hash()) set_state(true);
    });
  }

  $(".html-toggle.section > h2, .html-toggle.section > h3, .html-toggle.section > h4, .html-toggle.section > h5, .html-toggle.section > h6").each(init);
});
/* ==========================================================================
 * collapsible sidebar
 * ==========================================================================
 *
 * Adds button for collapsing & expanding sidebar,
 * which toggles "document.collapsed-sidebar" CSS class,
 * and relies on CSS for actual styling of visible & hidden sidebars.
 */

$(document).ready(function (){
  if(!$('.sphinxsidebar').length){
    return;
  }
  
    var close_arrow = '&laquo;';
    var open_arrow = 'sidebar &raquo;';
  
  var holder = $('<div class="sidebartoggle"><button id="sidebar-hide" title="click to hide the sidebar">' +
                 close_arrow + '</button><button id="sidebar-show" style="display: none" title="click to show the sidebar">' +
                 open_arrow + '</button></div>');
  var doc = $('div.document');

  var show_btn = $('#sidebar-show', holder);
  var hide_btn = $('#sidebar-hide', holder);
  /* FIXME: when url_root is a relative path, this sets cookie in wrong spot.
     need to detect relative roots, and combine with document.location.path */
  var copts = { expires: 7, path: DOCUMENTATION_OPTIONS.url_root };

  show_btn.click(function (){
    doc.removeClass("collapsed-sidebar");
    hide_btn.show();
    show_btn.hide();
    $.cookie("sidebar", "expanded", copts);
    $(window).trigger("cloud-sidebar-toggled", false);
  });

  hide_btn.click(function (){
    doc.addClass("collapsed-sidebar");
    show_btn.show();
    hide_btn.hide();
    $.cookie("sidebar", "collapsed", copts);
    $(window).trigger("cloud-sidebar-toggled", true);
  });

  var state = $.cookie("sidebar");


  doc.append(holder);

  if (state == "collapsed"){
    doc.addClass("collapsed-sidebar");
    show_btn.show();
    hide_btn.hide();
  }
});
/* ==========================================================================
 * sticky sidebar
 * ==========================================================================
 *
 * Instrument sidebar so that it sticks in place as page is scrolled.
 */
$(document).ready(function (){
  // initialize references to relevant elements
  var holder = $('.document'); // element that sidebar sits within
  var sidebar = $('.sphinxsidebar'); // element we're making "sticky"
  var toc_header = $('.sphinxlocaltoc h3'); // toc header + list control position
      if(!toc_header.length) toc_header = null;
  var toc_list = toc_header ? toc_header.next("ul") : null;
  var toggle = $('.sidebartoggle'); // also make collapse button sticky

  // initialize internal state
  var sticky_disabled = false; // whether sticky is disabled for given window size
  var sidebar_adjust = 0; // vertical offset within sidebar when sticky

  // offset() under jquery 1.4 is document-relative (sphinx 1.1), but
  // under jquery 1.5+ it's viewport-relative (sphinx 1.2 uses jquery 1.7).
  // since getBoundingClientRect is reasonbly cross-browser, using that instead.
  // getBoundClientRect is always viewport-relative.
  function left_offset($node){ return $node[0].getBoundingClientRect().left; }
  function top_offset($node){ return $node[0].getBoundingClientRect().top; }

  // function to set style for given state
  function set_style(target, value, adjust)
  {
    if(value <= adjust || sticky_disabled){
      target.css({marginLeft: "", position: "", top: "", left: "", bottom: ""});
    }
    else if (value <= holder.height() - target.height() + adjust){
      target.css({marginLeft: 0, position: "fixed", top: -adjust,
                 left: left_offset(holder), bottom: ""});
    }
    else{
      target.css({marginLeft: 0, position: "absolute", top: "", left: 0, bottom: 0});
    }
  }

  // func to update sidebar position based on scrollbar & container positions
  function update_sticky(){
    // set sidebar position
    var offset = -top_offset(holder);
    set_style(sidebar, offset, sidebar_adjust);
    // collapse button should follow along as well
    set_style(toggle, offset, 0);
  };

  // func to update sidebar measurements, and then call update_sticky()
  function update_measurements(){
    sticky_disabled = false;
    sidebar_adjust = 0;
    if(toc_header){
      // check how much room we have to display top of sidebar -> end of toc list
      var leftover = $(window).height() - (toc_list.height() + top_offset(toc_list) - top_offset(sidebar));
      if(leftover < 0){
        // not enough room if we align top of sidebar to window,
        // try aligning to top of toc list instead
        sidebar_adjust = top_offset(toc_header) - top_offset(sidebar) - 8;
        if(leftover + sidebar_adjust < 0){
          // still not enough room - disable sticky sidebar
          sticky_disabled = true;
        }
      }
    }
    update_sticky();
  }

  // run function now, and every time window scrolls
  update_measurements();
  $(window).scroll(update_sticky)
           .resize(update_measurements)
           .bind('cloud-section-toggled', update_measurements);
});


/* ==========================================================================
 * sidebar toc highlighter
 * ==========================================================================
 *
 * highlights toc entry for current section being viewed.
 */
$(document).ready(function (){

  // locate and scan sidebar's localtoc,
  // assembling metadata & relevant DOM nodes
  var records = [];
  var links = $(".sphinxlocaltoc > ul a");
  for(var i=0; i<links.length; ++i){
    var elem = $(links[i]);
    var tag = elem.attr("href");
    var section = (tag == "#") ? $("h1").parent() : $(tag);
    var children = section.find("div.section");
    records.push({elem: elem, // node used to store 'toggled' flag, always first node in <target>
                  target: elem, // set of local/global toc nodes to highlight
                  section: section, // dom node of referenced section
                  first_child: children.length ? $(children[0]) : null // first subsection of <section>
                  });
  }

  // locate and scan sidebar's globaltoc,
  // expanded <records> to include global toc nodes as well.
  var global_links = $(".sphinxglobaltoc > ul > li.current a");
  var l = records.length;
_global_toc_loop:
  for(var i=0; i<global_links.length; ++i){
    var elem = $(global_links[i]);
    var tag = elem.attr("href");
    if(tag && tag[0] != "#"){
      // it's a link to another document (embedded via toctree)
      // FIXME: would like to highlight these while hovering over their section
      continue;
    }
    var section = tag ? $(tag) : $("h1").parent();

    // add to existing localtoc record if one matched
    // (normal case if localtoc present)
    for(var j=0; j<l; ++j){
      var record = records[i];
      if(record.section[0] == section[0]){
        record.target = record.target.add(elem);
        continue _global_toc_loop;
      }
    }

    // or create new record (normal case if localtoc missing)
    var children = section.find("div.section");
    records.push({elem: elem, target: elem,
                  section: section,
                  first_child: children.length ? $(children[0]) : null
                  });
  }

  // abort if we couldn't find local -or- global toc
  if(!records.length) return;

  // from here on, <links> is only used to reset .toggled flag,
  // so merging global links in that list
  links = links.add(global_links);

  // replacement for $().offset() since that func isn't always viewport relative
  function top_offset($node){ return $node[0].getBoundingClientRect().top; }

  // function to update toc markers
  function update_visible_sections(){
    // determine viewable range
    var height = $(window).height();

    // helper to check if record is visible
    function is_visible(record){
      // hack to skip elements hidden w/in a toggled section
      if(record.elem.hasClass("toggled")) return false;

      // if section is off-screen, don't mark it
      var top = top_offset(record.section);
      if(top > height || top + record.section.height() < 0) return false;

      // if section has children, skip it once top of first subsection is offscreen
      if(record.first_child && top_offset(record.first_child) < 0) return false;

      // otherwise section is visible
      return true;
    }

    // set 'current' class for all currently viewable sections in toc
    for(var i=0; i < records.length; ++i){
      var record = records[i];
      record.target.toggleClass("visible", is_visible(record));
    }
  }

  // function to update is_hidden_child flag on records
  function update_collapsed_sections(){
    // clear toggled flag for all links
    links.removeClass("toggled");
    // re-add toggled flag for all links that are hidden w/in collapsed section
    for(var i=0; i < records.length; ++i){
      var record = records[i];
      if(record.section.is(".html-toggle.collapsed")){
        record.elem.parent().find("ul a").addClass("toggled");
      }
    }
    // redo highlight after flag rebuild
    update_visible_sections();
  }

  // run function now, and every time window is resized
  // TODO: disable when sidebar isn't sticky (including when window is too small)
  //       and when sidebar is collapsed / invisible
  update_collapsed_sections();
  $(window).scroll(update_visible_sections)
           .resize(update_visible_sections)
           .bind('cloud-section-toggled', update_collapsed_sections)
           .bind('cloud-sidebar-toggled', update_visible_sections);
});


/* ==========================================================================
 * header breaker
 * ==========================================================================
 *
 * attempts to intelligently insert linebreaks into page titles, where possible.
 * currently only handles titles such as "module - description",
 * adding a break after the "-".
 */
$(document).ready(function (){
  // get header's content, insert linebreaks
  var header = $("h1");
  var orig = header[0].innerHTML;
  var shorter = orig;
  if($("h1 > a:first > tt > span.pre").length > 0){
      shorter = orig.replace(/(<\/tt><\/a>\s*[-\u2013\u2014:]\s+)/im, "$1<br> ");
  }
  else if($("h1 > tt.literal:first").length > 0){
      shorter = orig.replace(/(<\/tt>\s*[-\u2013\u2014:]\s+)/im, "$1<br> ");
  }
  if(shorter == orig){
    return;
  }

  // hack to determine full width of header
  header.css({whiteSpace: "nowrap", position:"absolute"});
  var header_width = header.width();
  header.css({whiteSpace: "", position: ""});

  // func to insert linebreaks when needed
  function layout_header(){
    header[0].innerHTML = (header_width > header.parent().width()) ? shorter : orig;
  }

  // run function now, and every time window is resized
  layout_header();
  $(window).resize(layout_header)
           .bind('cloud-sidebar-toggled', layout_header);
});