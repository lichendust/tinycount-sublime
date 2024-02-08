import sublime
import sublime_plugin

STATUS_ID  = 'tinycount'
SIZE_LIMIT = 4194304

IGNORE_COMMENTS = True

def plugin_unloaded():
	for window in sublime.windows():
		for view in window.views():
			view.erase_status(STATUS_ID)

class Counter(sublime_plugin.EventListener):
	def __init__(self):
		self.is_active          = False
		self.has_selection      = False
		self.just_had_selection = False

	def do_word_count(self, view):
		view_size = view.size()

		if view_size > SIZE_LIMIT:
			view.set_status(STATUS_ID, "[!] Words")
			return

		word_count = 0

		# if we're dealing with a selection, loop over 'em all
		# and count within each individual region.
		if self.has_selection:
			for selection in view.sel():
				if len(selection) > 0:
					region = sublime.Region(selection.begin(), selection.end())
					word_count += len(view.substr(region).split())

		# otherwise do the whole thing using the total buffer size
		# as a region selection.
		else:
			for line in view.lines(sublime.Region(0, view_size)):
				# because scope_name accepts a point instead of a
				# region, we want to make sure that we're *inside*
				# the relevant region when we check for a comment.
				# we do this from the end of the line because most
				# comments (that we care about) will *run* to the
				# end of any given line. if we used the start,
				# we'd have to iterate over any possible whitespace
				# or indentation before we could be certain.
				# the line.b > line.a just ensures we don't clip
				# out of the intended regions on zero-width lines
				if IGNORE_COMMENTS and line.b > line.a and "comment" in view.scope_name(line.b - 1):
					continue

				word_count += len(view.substr(line).split())

		view.set_status(STATUS_ID, str(word_count) + " Words")

	def on_activated_async(self, view):
		self.is_active = view.window().is_status_bar_visible() and "text." in view.scope_name(0)

		if not self.is_active:
			# we're not unloading the plugin,
			# we're just calling the sublime
			# callback ourselves because it
			# does everything we need for this
			# step. might not always be true!
			plugin_unloaded()
			return

		self.do_word_count(view)

	def on_post_save_async(self, view):
		if not self.is_active:
			return

		self.do_word_count(view)

	def on_reload_async(self, view):
		if not self.is_active:
			return

		self.do_word_count(view)

	# maddeningly moving the caret without an active region selection
	# also fires this, so we do some extra work to reduce expenditure
	def on_selection_modified_async(self, view):
		if not self.is_active:
			return

		selection_total = 0
		for selection in view.sel():
			selection_total += len(selection)

		self.has_selection = selection_total > 0

		if self.has_selection:
			self.just_had_selection = True
			self.do_word_count(view)

		# this ensures a single reset when all
		# selections are cleared, otherwise
		# you're left with the last known
		# selection until a save or view change
		elif self.just_had_selection:
			self.do_word_count(view)
			self.just_had_selection = False
