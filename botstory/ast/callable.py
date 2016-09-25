import logging
from . import processor
from .. import matchers

logger = logging.getLogger(__name__)


@matchers.matcher()
class WaitForReturn:
    type = 'WaitForReturn'

    def __init__(self, immediately=False):
        # self.immediately = immediately
        pass

    def validate(self, message):
        # return 'return' in message
        return True


class EndOfStory:
    type = 'EndOfStory'

    def __init__(self, res):
        self.res = res


class CallableNodeWrapper:
    """
    helps start processing callable story
    """

    def __init__(self, ast_node, processor_instance):
        self.ast_node = ast_node
        self.processor_instance = processor_instance

    def startpoint(self, *args, **kwargs):
        if 'session' not in kwargs:
            raise AttributeError('Should pass session as well')

        session = kwargs.pop('session')

        # we are going deeper so prepare one more item in stack
        logger.debug('  action: extend stack by +1')
        session.stack.append(processor.build_empty_stack_item())
        return self.processor_instance.process_story(session,
                                                     # we don't have message yet
                                                     message=None,
                                                     compiled_story=self.ast_node,
                                                     idx=0,
                                                     story_args=args,
                                                     story_kwargs=kwargs)

        # return WaitForReturn()


class CallableStoriesAPI:
    def __init__(self, library, parser_instance, processor_instance):
        self.library = library
        self.parser_instance = parser_instance
        self.processor_instance = processor_instance

    def callable(self):
        def fn(callable_story):
            compiled_story = self.parser_instance.compile(
                callable_story,
            )
            self.library.add_callable(compiled_story)
            return CallableNodeWrapper(
                compiled_story,
                self.processor_instance
            ).startpoint

        return fn