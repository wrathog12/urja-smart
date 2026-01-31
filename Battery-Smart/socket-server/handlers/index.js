/**
 * Handler Index - Exports all handlers
 */

const sessionHandler = require('./sessionHandler');
const audioHandler = require('./audioHandler');
const chatHandler = require('./chatHandler');
const escalationHandler = require('./escalationHandler');

module.exports = {
  ...sessionHandler,
  ...audioHandler,
  ...chatHandler,
  ...escalationHandler
};
