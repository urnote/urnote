from note import objects


def run(args=None):
    controller = objects.get_controller()
    controller.run(args)
    objects.release()


if __name__ == '__main__':
    run()
