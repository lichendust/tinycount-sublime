import sublime
import sublime_plugin

import re

STATUS_ID  = 'tinycount'
SIZE_LIMIT = 4194304

IGNORE_COMMENTS = True

def plugin_unloaded():
	for window in sublime.windows():
		for view in window.views():
			view.erase_status(STATUS_ID)

class Counter(sublime_plugin.EventListener):
	def __init__(self):
		self.has_selection      = False
		self.just_had_selection = False

	def do_word_count(self, view):
		view_size = view.size()

		if view_size > SIZE_LIMIT:
			view.set_status(STATUS_ID, "Word Count [Too Large]")
			return

		word_count = 0

		if self.has_selection:
			for selection in view.sel():
				if len(selection) > 0:
					region = sublime.Region(selection.begin(), selection.end())
					word_count += len(view.substr(region).split())

		else:
			for line in view.lines(sublime.Region(0, view_size)):
				if IGNORE_COMMENTS and line.b > line.a and "comment" in view.scope_name(line.b - 1):
					continue

				word_count += len(view.substr(line).split())

		view.set_status(STATUS_ID, str(word_count) + " Words")

	def on_activated_async(self, view):
		self.do_word_count(view)

	def on_activated_async(self, view):
		self.do_word_count(view)

	def on_post_save_async(self, view):
		self.do_word_count(view)

	def on_reload_async(self, view):
		self.do_word_count(view)

	def on_selection_modified_async(self, view):
		selection_total = 0
		for selection in view.sel():
			selection_total += len(selection)

		# this just massively reduces how many
		# times this can run -- it'll happen
		# once per full selection change rather
		# than every single time the caret moves

		self.has_selection = selection_total > 0

		if self.has_selection:
			self.just_had_selection = True
			self.do_word_count(view)
		elif self.just_had_selection:
			self.do_word_count(view)
			self.just_had_selection = False
