export const LoadingWhitelist = () => {
  return (
    <div className="m-auto">
      <div className="relative flex h-8 w-8 items-center justify-center">
        <h1 className="sr-only">Loading...</h1>
        <div className="ripple border-black animate-ripple absolute h-8 w-8 rounded-full border-2"></div>
        <div className="ripple border-black animate-ripple-delay absolute h-8 w-8 rounded-full border-2"></div>
      </div>
    </div>
  );
};
