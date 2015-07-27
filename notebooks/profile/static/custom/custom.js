// leave at least 2 line with only a star on it below, or doc generation fails
/**
 *
 *
 * Placeholder for custom user javascript
 * mainly to be overridden in profile/static/custom/custom.js
 * This will always be an empty file in IPython
 *
 * User could add any javascript in the `profile/static/custom/custom.js` file
 * (and should create it if it does not exist).
 * It will be executed by the ipython notebook at load time.
 *
 * Same thing with `profile/static/custom/custom.css` to inject custom css into the notebook.
 *
 * Example :
 *
 * Create a custom button in toolbar that execute `%qtconsole` in kernel
 * and hence open a qtconsole attached to the same kernel as the current notebook
 *
 *    $([IPython.events]).on('app_initialized.NotebookApp', function(){
 *        IPython.toolbar.add_buttons_group([
 *            {
 *                 'label'   : 'run qtconsole',
 *                 'icon'    : 'icon-terminal', // select your icon from http://fortawesome.github.io/Font-Awesome/icons
 *                 'callback': function () {
 *                     IPython.notebook.kernel.execute('%qtconsole')
 *                 }
 *            }
 *            // add more button here if needed.
 *            ]);
 *    });
 *
 * Example :
 *
 *  Use `jQuery.getScript(url [, success(script, textStatus, jqXHR)] );`
 *  to load custom script into the notebook.
 *
 *    // to load the metadata ui extension example.
 *    $.getScript('/static/notebook/js/celltoolbarpresets/example.js');
 *    // or
 *    // to load the metadata ui extension to control slideshow mode / reveal js for nbconvert
 *    $.getScript('/static/notebook/js/celltoolbarpresets/slideshow.js');
 *
 *
 * @module IPython
 * @namespace IPython
 * @class customjs
 * @static
 */

require(['codemirror/lib/codemirror', 'codemirror/mode/meta'], function(cm){
  for(var i=0; i<cm.modeInfo.length; i++){ 
    if (cm.modeInfo[i].name=='Shell'){
      cm.modeInfo[i].ext.push('bsh')
    }
    else if(cm.modeInfo[i].name=='Dockerfile'){
      cm.modeInfo[i].ext =['dockerfile']
    }
  }
})

require(["codemirror/addon/display/rulers"], function(){
  var rulers = [{column: 79},
                {column: 80}];
 
  $([IPython.events]).on('app_initialized.NotebookApp', function(){
    IPython.Cell.options_default.cm_config.rulers = rulers;})
  
  require(['edit/js/editor'], function (e){e.Editor.default_codemirror_options.rulers = rulers;})
})

$([IPython.events]).on('file_loaded.Editor', function(){ 
  cm = IPython.editor.codemirror
  cm.options.indentUnit=2
  cm.options.tabSize=2
  
  if (cm.options.mode == 'null'){
    require(['codemirror/lib/codemirror', 'codemirror/mode/meta'], function(cm_full){
      actual_mode = cm_full.findModeByName(IPython.editor.file_path.split('/').pop())
      if (actual_mode){
        IPython.editor.set_codemirror_mode(actual_mode)
      }
    })
  }
});

$([IPython.events]).on('app_initialized.NotebookApp', function(){ 
  IPython.Cell.options_default.cm_config.indentUnit = 2;
  IPython.Cell.options_default.cm_config.lineNumbers = true;
  IPython.CodeCell.options_default.cm_config.autoCloseBrackets = false;

  var autoRunAllOnKernelReady = false
  
  var autoRunAll = function(){
    if (autoRunAllOnKernelReady)
    {
      autoRunAllOnKernelReady = false;
      console.log('OH NO!');
      IPython.notebook.execute_all_cells();
    }
    console.log('kwernel ready')
  }
  
  $([IPython.events]).on('kernel_ready.Kernel', autoRunAll)
  
  var restartAndRunAll = function(){
    autoRunAllOnKernelReady = true;
    IPython.notebook.kernel.restart();
  }

  IPython.toolbar.add_buttons_group([
    {
      'label'   : 'Restart and run all',
      'icon'    : 'fa-undo', // select your icon from http://fortawesome.github.io/Font-Awesome/icons
      'callback': restartAndRunAll
    }
    // add more button here if needed.
  ]);
});
