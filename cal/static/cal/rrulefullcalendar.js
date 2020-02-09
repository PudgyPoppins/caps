/*!
FullCalendar RRule Plugin v4.3.0
Docs & License: https://fullcalendar.io/
(c) 2019 Adam Shaw
*/
!function(e,r){"object"==typeof exports&&"undefined"!=typeof module?r(exports,require("rrule"),require("@fullcalendar/core")):"function"==typeof define&&define.amd?define(["exports","rrule","@fullcalendar/core"],r):r((e=e||self).FullCalendarRrule={},e.rrule,e.FullCalendar)}(this,function(e,r,t){"use strict";var n=function(){return(n=Object.assign||function(e){for(var r,t=1,n=arguments.length;t<n;t++)for(var u in r=arguments[t])Object.prototype.hasOwnProperty.call(r,u)&&(e[u]=r[u]);return e}).apply(this,arguments)},u={rrule:null,duration:t.createDuration},l={parse:function(e,l,a){if(null!=e.rrule){var f=t.refineProps(e,u,{},l),o=function(e,t){var u,l=null;if("string"==typeof e)u=r.rrulestr(e);else if("object"==typeof e&&e){var a=n({},e);if("string"==typeof a.dtstart){var f=t.createMarkerMeta(a.dtstart);f?(a.dtstart=f.marker,l=f.isTimeUnspecified):delete a.dtstart}"string"==typeof a.until&&(a.until=t.createMarker(a.until)),null!=a.freq&&(a.freq=i(a.freq)),null!=a.wkst?a.wkst=i(a.wkst):a.wkst=(t.weekDow-1+7)%7,null!=a.byweekday&&(a.byweekday=function(e){if(Array.isArray(e))return e.map(i);return i(e)}(a.byweekday)),u=new r.RRule(a)}if(u)return{rrule:u,allDayGuess:l};return null}(f.rrule,a);if(o)return{typeData:o.rrule,allDayGuess:o.allDayGuess,duration:f.duration}}return null},expand:function(e,r){return e.between(r.start,r.end,!0).filter(function(e){return e.valueOf()<r.end.valueOf()})}},a=t.createPlugin({recurringTypes:[l]});function i(e){return"string"==typeof e?r.RRule[e.toUpperCase()]:e}e.default=a,Object.defineProperty(e,"__esModule",{value:!0})});