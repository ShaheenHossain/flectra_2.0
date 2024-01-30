/**
 * This file allows introducing new JS modules without contaminating other files.
 * This is useful when bug fixing requires adding such JS modules in stable
 * versions of Flectra. Any module that is defined in this file should be isolated
 * in its own file in master.
 */
flectra.define('sms/static/src/bugfix/bugfix.js', function (require) {
'use strict';

});